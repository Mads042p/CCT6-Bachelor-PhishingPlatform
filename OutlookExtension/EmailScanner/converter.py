import os
import torch
import torch.nn as nn

# Load the PyTorch model file modelText.pt located next to this script
model_path = os.path.join(os.path.dirname(__file__), "modelText.pt")

class GRU(nn.Module):
    """RNN Model similar to LSTM but fewer parameters. Faster and easier to train. Potentially better for small features, not long text pieces."""
    def __init__(self, vocab_size, embed_dim, hidden_dim, output_dim, n_layers=1):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.gru = nn.GRU(embed_dim, hidden_dim, num_layers=n_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, text):
        embedded = self.embedding(text)
        output, hidden = self.gru(embedded)
        hidden = hidden.squeeze(0)
        return self.fc(hidden)
    
model = GRU(vocab_size=20000, embed_dim=128, hidden_dim=128, output_dim=2, n_layers=1)
model.load_state_dict(torch.load(model_path, map_location="cpu"))
model.eval()

# If the file contains only a state_dict, the user should load it into a model class.
# Here we assume the file contains a full serialized model object.

dummy_input = torch.randint(
    0,
    20000,
    (1, 128),
    dtype=torch.long
)

torch.onnx.export(
    model,
    dummy_input,
    "phishing_model.onnx",

    input_names=["input"],
    output_names=["output"],

    dynamic_axes={
        "input": {
            1: "batch_size"
        },
        "output": {
            1: "batch_size"
        }
    },

    opset_version=17,

    dynamo=False
)