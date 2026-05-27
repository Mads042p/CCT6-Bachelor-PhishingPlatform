import json
import re
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader


CSV_PATH = "Phishing_Email.csv"
VOCAB_PATH = "vocab.json"

MAX_LEN = 128
BATCH_SIZE = 32
EPOCHS = 5
LR = 1e-3


with open(VOCAB_PATH, "r", encoding="utf-8") as f:
    vocab = json.load(f)

PAD_TOKEN = "<PAD>"
UNK_TOKEN = "<UNK>"

PAD_ID = vocab.get(PAD_TOKEN, 0)
UNK_ID = vocab.get(UNK_TOKEN, 1)


def tokenize(text):
    return re.findall(r"[a-z0-9']+", str(text).lower())


def encode(text):
    tokens = tokenize(text)

    ids = [vocab.get(t, UNK_ID) for t in tokens]

    ids = ids[:MAX_LEN]

    if len(ids) < MAX_LEN:
        ids += [PAD_ID] * (MAX_LEN - len(ids))

    return ids


def convert_label(label):
    label = str(label).strip().lower()

    if label == "phishing email":
        return 1.0
    elif label == "safe email":
        return 0.0
    else:
        raise ValueError(f"Unknown label: {label}")


class EmailDataset(Dataset):
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        text = self.df.iloc[idx]["Email Text"]
        label = self.df.iloc[idx]["Email Type"]

        x = torch.tensor(encode(text), dtype=torch.long)
        y = torch.tensor(convert_label(label), dtype=torch.float32)

        return x, y


class GRUModel(nn.Module):
    def __init__(self, vocab_size, embed_dim=128, hidden_dim=128):
        super().__init__()

        self.embedding = nn.Embedding(vocab_size, embed_dim)

        self.gru = nn.GRU(
            embed_dim,
            hidden_dim,
            batch_first=True
        )

        self.fc = nn.Linear(hidden_dim, 1)

    def forward(self, x):

        x = self.embedding(x)

        _, h = self.gru(x)

        out = self.fc(h[-1])

        return out.squeeze(1)  # logits


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

dataset = EmailDataset(CSV_PATH)
loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

model = GRUModel(vocab_size=len(vocab)).to(device)

criterion = nn.BCEWithLogitsLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LR)


model.train()

for epoch in range(EPOCHS):

    total_loss = 0

    for x, y in loader:

        x, y = x.to(device), y.to(device)

        optimizer.zero_grad()

        logits = model(x)

        loss = criterion(logits, y)

        loss.backward()

        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch+1}/{EPOCHS} - Loss: {total_loss:.4f}")


torch.save(model.state_dict(), "phishing_gru.pt")
print("PyTorch model saved")


model.eval()

dummy_input = torch.randint(
    0,
    len(vocab),
    (1, MAX_LEN),
    dtype=torch.long
).to(device)

torch.onnx.export(
    model,
    dummy_input,
    "phishing_model.onnx",

    input_names=["input"],
    output_names=["output"],

    dynamic_axes={
        "input": {0: "batch_size"},
        "output": {0: "batch_size"}
    },

    opset_version=17,
    dynamo=False
)

print("ONNX export complete → phishing_model.onnx")