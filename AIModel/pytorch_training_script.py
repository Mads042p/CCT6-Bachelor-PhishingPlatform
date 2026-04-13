from AIModelsTorch import RNN, LSTM, GRU
import argparse
import random
import re
from collections import Counter

import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
import json
import os
from google.cloud import storage


CSV_PATH = "Phishing_Email.csv"
TEXT_COLUMN = "Email Text"
LABEL_COLUMN = "Email Type"

MODEL_SAVE_PATH = "model.pt"
VOCAB_SAVE_PATH = "vocab.json"

SEED = 42
MAX_VOCAB_SIZE = 20000
MAX_SEQ_LEN = 200
BATCH_SIZE = 64
EMBED_DIM = 128
HIDDEN_DIM = 128
N_LAYERS = 1
LR = 1e-3
EPOCHS = 5

PAD_TOKEN = "<pad>"
UNK_TOKEN = "<unk>"


def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("--csv_path", default=CSV_PATH)
	parser.add_argument("--model_output", default=MODEL_SAVE_PATH)
	parser.add_argument("--vocab_output", default=VOCAB_SAVE_PATH)
	return parser.parse_args()


def parse_gs_uri(uri: str):
	if not uri.startswith("gs://"):
		raise ValueError(f"Not a GCS URI: {uri}")
	without_scheme = uri[5:]
	bucket_name, blob_name = without_scheme.split("/", 1)
	return bucket_name, blob_name


def resolve_input_path(path: str, local_filename: str):
	if not path.startswith("gs://"):
		return path
	bucket_name, blob_name = parse_gs_uri(path)
	storage.Client().bucket(bucket_name).blob(blob_name).download_to_filename(local_filename)
	return local_filename


def save_output(local_path: str, destination_path: str):
	if destination_path.startswith("gs://"):
		bucket_name, blob_name = parse_gs_uri(destination_path)
		storage.Client().bucket(bucket_name).blob(blob_name).upload_from_filename(local_path)
	else:
		if os.path.dirname(destination_path):
			os.makedirs(os.path.dirname(destination_path), exist_ok=True)
		if local_path != destination_path:
			os.replace(local_path, destination_path)


def set_seed(seed: int) -> None:
	random.seed(seed)
	torch.manual_seed(seed)
	if torch.cuda.is_available():
		torch.cuda.manual_seed_all(seed)


def tokenize(text: str):
	return re.findall(r"[a-z0-9']+", str(text).lower())


def build_vocab(texts, max_vocab_size: int):
	counter = Counter()
	for text in texts:
		counter.update(tokenize(text))

	vocab = {PAD_TOKEN: 0, UNK_TOKEN: 1}
	for token, _ in counter.most_common(max_vocab_size - len(vocab)):
		vocab[token] = len(vocab)
	return vocab


def encode_text(text: str, vocab, max_len: int):
	token_ids = [vocab.get(token, vocab[UNK_TOKEN]) for token in tokenize(text)]
	token_ids = token_ids[:max_len]
	if len(token_ids) < max_len:
		token_ids += [vocab[PAD_TOKEN]] * (max_len - len(token_ids))
	return token_ids


class EmailDataset(Dataset):
	def __init__(self, texts, labels, vocab, max_len):
		self.encoded_texts = [encode_text(text, vocab, max_len) for text in texts]
		self.labels = labels

	def __len__(self):
		return len(self.labels)

	def __getitem__(self, idx):
		text_tensor = torch.tensor(self.encoded_texts[idx], dtype=torch.long)
		label_tensor = torch.tensor(self.labels[idx], dtype=torch.long)
		return text_tensor, label_tensor


def split_data(df: pd.DataFrame, train_ratio=0.7, val_ratio=0.15):
	df = df.sample(frac=1.0, random_state=SEED).reset_index(drop=True)
	n = len(df)
	n_train = int(n * train_ratio)
	n_val = int(n * val_ratio)

	train_df = df.iloc[:n_train]
	val_df = df.iloc[n_train:n_train + n_val]
	test_df = df.iloc[n_train + n_val:]
	return train_df, val_df, test_df


def run_epoch(model, loader, criterion, optimizer, device):
	model.train()
	total_loss = 0.0
	total_correct = 0
	total_examples = 0

	for inputs, targets in loader:
		inputs = inputs.to(device)
		targets = targets.to(device)

		optimizer.zero_grad()
		logits = model(inputs)
		loss = criterion(logits, targets)
		loss.backward()
		optimizer.step()

		total_loss += loss.item() * targets.size(0)
		predictions = logits.argmax(dim=1)
		total_correct += (predictions == targets).sum().item()
		total_examples += targets.size(0)

	return total_loss / total_examples, total_correct / total_examples


@torch.no_grad()
def evaluate(model, loader, criterion, device):
	model.eval()
	total_loss = 0.0
	total_correct = 0
	total_examples = 0

	for inputs, targets in loader:
		inputs = inputs.to(device)
		targets = targets.to(device)

		logits = model(inputs)
		loss = criterion(logits, targets)

		total_loss += loss.item() * targets.size(0)
		predictions = logits.argmax(dim=1)
		total_correct += (predictions == targets).sum().item()
		total_examples += targets.size(0)

	return total_loss / total_examples, total_correct / total_examples


def main():
	print("Starting training...")
	args = parse_args()
	set_seed(SEED)
	device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

	csv_path = resolve_input_path(args.csv_path, "training_data.csv")
	df = pd.read_csv(csv_path)
	df = df[[TEXT_COLUMN, LABEL_COLUMN]].dropna()
	label_map = {"Safe Email": 0, "Phishing Email": 1}
	df = df[df[LABEL_COLUMN].isin(label_map.keys())].copy()
	df["label"] = df[LABEL_COLUMN].map(label_map)

	train_df, val_df, test_df = split_data(df)
	vocab = build_vocab(train_df[TEXT_COLUMN].tolist(), MAX_VOCAB_SIZE)

	train_dataset = EmailDataset(
		train_df[TEXT_COLUMN].tolist(),
		train_df["label"].tolist(),
		vocab,
		MAX_SEQ_LEN,
	)
	val_dataset = EmailDataset(
		val_df[TEXT_COLUMN].tolist(),
		val_df["label"].tolist(),
		vocab,
		MAX_SEQ_LEN,
	)
	test_dataset = EmailDataset(
		test_df[TEXT_COLUMN].tolist(),
		test_df["label"].tolist(),
		vocab,
		MAX_SEQ_LEN,
	)
	print("Train, Val, Test datasets created.")

	train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
	val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)
	test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)

	model = GRU(
		vocab_size=len(vocab),
		embed_dim=EMBED_DIM,
		hidden_dim=HIDDEN_DIM,
		output_dim=2,
		n_layers=N_LAYERS,
	).to(device)

	criterion = nn.CrossEntropyLoss()
	optimizer = torch.optim.Adam(model.parameters(), lr=LR)

	print(f"Using device: {device}")
	print(f"Train/Val/Test sizes: {len(train_dataset)}/{len(val_dataset)}/{len(test_dataset)}")
	print(f"Vocabulary size: {len(vocab)}")

	best_val_acc = 0.0
	best_state = None

	for epoch in range(1, EPOCHS + 1):
		train_loss, train_acc = run_epoch(model, train_loader, criterion, optimizer, device)
		val_loss, val_acc = evaluate(model, val_loader, criterion, device)
		print(
			f"Epoch {epoch}/{EPOCHS} | "
			f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | "
			f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}"
		)

		if val_acc > best_val_acc:
			best_val_acc = val_acc
			best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

	if best_state is not None:
		model.load_state_dict(best_state)

	test_loss, test_acc = evaluate(model, test_loader, criterion, device)
	print(f"Test Loss: {test_loss:.4f} | Test Acc: {test_acc:.4f}")

	# Save model and vocabulary
	local_model_path = "model.pt"
	local_vocab_path = "vocab.json"
	torch.save(model.state_dict(), local_model_path)
	with open(local_vocab_path, 'w') as f:
		json.dump(vocab, f)

	save_output(local_model_path, args.model_output)
	save_output(local_vocab_path, args.vocab_output)
	print(f"Model saved to {args.model_output}")
	print(f"Vocabulary saved to {args.vocab_output}")


if __name__ == "__main__":
	main()


