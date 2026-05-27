const ort = require("onnxruntime-web");

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

    document.getElementById("sideload-msg").style.display = "none";
    document.getElementById("app-body").style.display = "flex";


    // Load model
    session = await ort.InferenceSession.create(
      "/assets/phishing_model.onnx",
      {
        executionProviders: ["wasm"],
      }
    );

    console.log("ONNX model loaded");

    //Load vocabulary
    const response = await fetch(
      "/assets/vocab.json"
    );

    vocab = await response.json();

    console.log("Vocabulary loaded");

    document.getElementById("run").onclick = run;
  }
});



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

  // decrease to 128 tokens
  tokenIds = tokenIds.slice(0, MAX_LEN);

  // pad to 128 tokens
  while (tokenIds.length < MAX_LEN) {
    tokenIds.push(vocab[PAD_TOKEN]);
  }

  return tokenIds;
}



async function run() {

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

      // Get email body text
      const emailText = result.value;

      console.log(emailText);

      const modelInput = encodeText(emailText);

      console.log(modelInput);


      // build input tensor
      const inputTensor = new ort.Tensor(
        "int64",
        BigInt64Array.from(modelInput.map((id) => BigInt(id))),
        [1, MAX_LEN]
      );

      // run model
      let outputs;
      try {
        outputs = await session.run({ input: inputTensor });
      } catch (err) {
        console.error('Model run failed', err);
        return;
      }

      // compute sigmoid of model output
      const raw = outputs.output && outputs.output.data ? outputs.output.data[0] : outputs[0];
      const prediction = 1 / (1 + Math.exp(-raw));

      console.log("Prediction:", prediction);

      const statusEl = document.getElementById('prediction-status');
      const confEl = document.getElementById('prediction-confidence');

      if (!statusEl) {
        console.error('Missing #prediction-status element in task pane HTML.');
        return;
      }

      // Update UI based on threshold
      const probability = (prediction * 100).toFixed(2);
      if (prediction >= 0.4) {
        statusEl.className = 'prediction-status pred-phishing';
        statusEl.innerText = '⚠️ PHISHING DETECTED\nREVIEW CAREFULLY AND REPORT IF SUSPICIOUS\n DO NOT CLICK LINKS OR DOWNLOAD ATTACHMENTS';

        confEl.style.display = 'block';
        confEl.innerText = `Confidence: ${probability}%`;
      } else {
        statusEl.className = 'prediction-status pred-safe';
        statusEl.innerText = '✅ SAFE EMAIL';

        // hide confidence when not phishing
        confEl.style.display = 'none';
        confEl.innerText = '';
      }
    }
  );
}