const ort = require("onnxruntime-web");
//import * as ort from "onnxruntime-web";

ort.env.wasm.simd = false;
ort.env.wasm.numThreads = 1;
ort.env.wasm.wasmPaths = "https://cdn.jsdelivr.net/npm/onnxruntime-web/dist/";

let session;
let vocab = null;

const MAX_LEN = 128;
const PAD_TOKEN = "<pad>";
const UNK_TOKEN = "<unk>";

Office.onReady(async (info) => {

  if (info.host === Office.HostType.Outlook) {
    // -----------------------------------
    // LOAD ONNX MODEL
    // -----------------------------------

    session = await ort.InferenceSession.create(
      "/assets/phishing_model.onnx",
      {
        executionProviders: ["wasm"],
      }
    );

    console.log("ONNX model loaded");

    // -----------------------------------
    // LOAD VOCAB
    // -----------------------------------

    const response = await fetch(
      "/assets/vocab.json"
    );

    vocab = await response.json();

    console.log("Vocabulary loaded");
  }
});


/**
 * Shows a notification when the add-in command is executed.
 * @param event {Office.AddinCommands.Event}
 */
async function action(event) {

  const item = Office.context.mailbox.item;

  item.body.getAsync(
    Office.CoercionType.Text,

    async function(result) {

      if (
        result.status !==
        Office.AsyncResultStatus.Succeeded
      ) {
        console.error(result.error.message);
        return;
      }

      // -----------------------------------
      // EMAIL TEXT
      // -----------------------------------

      const emailText = result.value;

      console.log(emailText);

      // -----------------------------------
      // TOKENIZE + ENCODE
      // -----------------------------------

      const inputIds = encodeText(emailText);

      console.log(inputIds);

      // -----------------------------------
      // CREATE TENSOR
      // -----------------------------------

      const tensor = new ort.Tensor(
        "int64",

        BigInt64Array.from(
          inputIds.map(id => BigInt(id))
        ),

        [1, MAX_LEN]
      );

      // -----------------------------------
      // RUN INFERENCE
      // -----------------------------------

      const outputs = await session.run({
        input: tensor
      });

      // IMPORTANT:
      // "output" must match your ONNX output name

      const prediction =
        outputs.output.data[0];

      console.log("Prediction:", prediction);

      // -----------------------------------
      // DISPLAY RESULT
      // -----------------------------------

      if (prediction >= 0.5) {
          const message = {
            type: Office.MailboxEnums.ItemNotificationMessageType.InformationalMessage,
            message: "Phishing detected: " + prediction,
            icon: "Icon.80x80",
            persistent: true,
          };
      } else {
          const message = {
            type: Office.MailboxEnums.ItemNotificationMessageType.InformationalMessage,
            message: "Not phishing: " + prediction,
            icon: "Icon.80x80",
            persistent: true,
          };
      }
    




      // Show a notification message.
      Office.context.mailbox.item.notificationMessages.replaceAsync(
        "ActionPerformanceNotification",
        message
      );

      // Be sure to indicate when the add-in command function is complete.
      event.completed();
    }
  );
}

// Register the function with Office.
Office.actions.associate("action", action);



function tokenize(text) {

  return text
    .toLowerCase()
    .match(/[a-z0-9']+/g) || [];
}


function encodeText(text) {

  const tokens = tokenize(text);

  let tokenIds = tokens.map(token =>
    vocab[token] ?? vocab[UNK_TOKEN]
  );

  // truncate to 128 tokens
  tokenIds = tokenIds.slice(0, MAX_LEN);

  // pad to 128 tokens
  while (tokenIds.length < MAX_LEN) {
    tokenIds.push(vocab[PAD_TOKEN]);
  }

  return tokenIds;
}