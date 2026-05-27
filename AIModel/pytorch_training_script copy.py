import argparse
import json
import os
import random
import re
from collections import Counter

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from torch.utils.data import DataLoader, Dataset

from AIModelsTorch import GRU, LSTM, RNN



CSV_PATH = "senderDataset.csv"
TEXT_COLUMN = "sender"
LABEL_COLUMN = "label"

MODEL_SAVE_PATH = "model.pt"
VOCAB_SAVE_PATH = "vocab.json"
VOCABLETTERS_PATH = "vocabletters.json"
OUTPUT_DIR = "training_outputs"

SEED = 42
MAX_VOCAB_SIZE = 20000
MAX_SEQ_LEN = 200
BATCH_SIZE = 64
EMBED_DIM = 128
HIDDEN_DIM = 128
N_LAYERS = 1
LR = 1e-3
EPOCHS = 5
AE_EPOCHS = 12
AE_BATCH_SIZE = 128
AE_LR = 1e-3
PROGRESS_BATCH_EVERY = 50

PAD_TOKEN = "<pad>"
UNK_TOKEN = "<unk>"


def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("--csv_path", default=CSV_PATH)
	parser.add_argument("--model_output", default=MODEL_SAVE_PATH)
	parser.add_argument("--vocab_output", default=VOCAB_SAVE_PATH)
	parser.add_argument("--output_dir", default=OUTPUT_DIR)
	return parser.parse_args()


def validate_local_path(path: str, path_name: str):
	if path.startswith("gs://"):
		raise ValueError(f"{path_name} must be a local path, got: {path}")


def save_output(local_path: str, destination_path: str):
	if os.path.dirname(destination_path):
		os.makedirs(os.path.dirname(destination_path), exist_ok=True)
	if local_path != destination_path:
		os.replace(local_path, destination_path)


def save_json_output(data, destination_path: str):
	local_tmp_path = "_tmp_output.json"
	with open(local_tmp_path, "w", encoding="utf-8") as f:
		json.dump(data, f, indent=2)
	save_output(local_tmp_path, destination_path)


def set_seed(seed: int) -> None:
	random.seed(seed)
	torch.manual_seed(seed)
	if torch.cuda.is_available():
		torch.cuda.manual_seed_all(seed)


def tokenize(text: str):
	# character-level tokenization: return each character (lowercased)
	return list(str(text).lower())


def build_vocab(texts, max_vocab_size: int):
	# fallback builder that creates a dense index from encountered characters
	counter = Counter()
	for text in texts:
		counter.update(tokenize(text))

	vocab = {PAD_TOKEN: 0, UNK_TOKEN: 1}
	for token, _ in counter.most_common(max_vocab_size - len(vocab)):
		vocab[token] = len(vocab)
	return vocab


def load_vocabletters(path: str):
	"""Load `vocabletters.json` and convert to a dense index mapping suitable for nn.Embedding.

	The source file may map characters to Unicode codepoints; this function ignores those
	integer values and instead returns a compact mapping: PAD=0, UNK=1, then sequential
	indices for the remaining characters.
	"""
	if not os.path.exists(path):
		raise FileNotFoundError(f"Vocabletters file not found: {path}")

	with open(path, "r", encoding="utf-8") as f:
		raw = json.load(f)

	vocab = {PAD_TOKEN: 0, UNK_TOKEN: 1}
	idx = 2
	# keep deterministic order: sort keys excluding PAD/UNK
	for k in sorted(raw.keys()):
		if k in (PAD_TOKEN, UNK_TOKEN):
			continue
		vocab[k] = idx
		idx += 1

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
	temp_ratio = 1.0 - train_ratio
	train_df, temp_df = train_test_split(
		df,
		test_size=temp_ratio,
		random_state=SEED,
		stratify=df["label"],
	)
	test_ratio_of_temp = (1.0 - train_ratio - val_ratio) / temp_ratio
	val_df, test_df = train_test_split(
		temp_df,
		test_size=test_ratio_of_temp,
		random_state=SEED,
		stratify=temp_df["label"],
	)

	train_df = train_df.reset_index(drop=True)
	val_df = val_df.reset_index(drop=True)
	test_df = test_df.reset_index(drop=True)
	return train_df, val_df, test_df


def run_epoch(model, loader, criterion, optimizer, device):
	model.train()
	total_loss = 0.0
	total_correct = 0
	total_examples = 0
	total_batches = len(loader)

	for batch_idx, (inputs, targets) in enumerate(loader, start=1):
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

		if batch_idx % PROGRESS_BATCH_EVERY == 0 or batch_idx == total_batches:
			print(
				f"  Training batch {batch_idx}/{total_batches} | "
				f"Running Loss: {total_loss / max(total_examples, 1):.4f} | "
				f"Running Acc: {total_correct / max(total_examples, 1):.4f}"
			)

	return total_loss / total_examples, total_correct / total_examples


@torch.no_grad()
def evaluate(model, loader, criterion, device):
	model.eval()
	total_loss = 0.0
	total_correct = 0
	total_examples = 0
	total_batches = len(loader)

	for batch_idx, (inputs, targets) in enumerate(loader, start=1):
		inputs = inputs.to(device)
		targets = targets.to(device)

		logits = model(inputs)
		loss = criterion(logits, targets)

		total_loss += loss.item() * targets.size(0)
		predictions = logits.argmax(dim=1)
		total_correct += (predictions == targets).sum().item()
		total_examples += targets.size(0)

		if batch_idx % PROGRESS_BATCH_EVERY == 0 or batch_idx == total_batches:
			print(
				f"  Eval batch {batch_idx}/{total_batches} | "
				f"Running Loss: {total_loss / max(total_examples, 1):.4f} | "
				f"Running Acc: {total_correct / max(total_examples, 1):.4f}"
			)

	return total_loss / total_examples, total_correct / total_examples


@torch.no_grad()
def predict_torch_model(model, loader, device):
	model.eval()
	predictions = []
	for inputs, _ in loader:
		inputs = inputs.to(device)
		logits = model(inputs)
		predictions.extend(logits.argmax(dim=1).cpu().tolist())
	return np.array(predictions)


def train_torch_classifier(model_name, model, train_loader, val_loader, test_loader, device):
	criterion = nn.CrossEntropyLoss()
	optimizer = torch.optim.Adam(model.parameters(), lr=LR)

	best_val_acc = 0.0
	best_state = None

	for epoch in range(1, EPOCHS + 1):
		print(f"[{model_name}] Starting epoch {epoch}/{EPOCHS}...")
		train_loss, train_acc = run_epoch(model, train_loader, criterion, optimizer, device)
		val_loss, val_acc = evaluate(model, val_loader, criterion, device)
		print(
			f"[{model_name}] Epoch {epoch}/{EPOCHS} | "
			f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | "
			f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}"
		)

		if val_acc > best_val_acc:
			best_val_acc = val_acc
			best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

	if best_state is not None:
		model.load_state_dict(best_state)

	test_loss, test_acc = evaluate(model, test_loader, criterion, device)
	test_preds = predict_torch_model(model, test_loader, device)
	print(f"[{model_name}] Test Loss: {test_loss:.4f} | Test Acc: {test_acc:.4f}")

	return {
		"best_state": best_state,
		"test_loss": test_loss,
		"test_acc": test_acc,
		"test_preds": test_preds,
	}


class Autoencoder(nn.Module):
	def __init__(self, input_dim, latent_dim=64):
		super().__init__()
		self.encoder = nn.Sequential(
			nn.Linear(input_dim, 256),
			nn.ReLU(),
			nn.Linear(256, latent_dim),
			nn.ReLU(),
		)
		self.decoder = nn.Sequential(
			nn.Linear(latent_dim, 256),
			nn.ReLU(),
			nn.Linear(256, input_dim),
		)

	def forward(self, x):
		z = self.encoder(x)
		return self.decoder(z)


def reconstruction_errors(model, features, device):
	model.eval()
	with torch.no_grad():
		x = torch.tensor(features, dtype=torch.float32, device=device)
		recon = model(x)
		errors = torch.mean((recon - x) ** 2, dim=1)
	return errors.cpu().numpy()


def train_autoencoder_and_predict(
	X_train_dense,
	y_train,
	X_val_dense,
	y_val,
	X_test_dense,
	device,
):
	safe_train_mask = y_train == 1
	X_train_ae = X_train_dense[safe_train_mask]
	if X_train_ae.shape[0] == 0:
		X_train_ae = X_train_dense

	model = Autoencoder(input_dim=X_train_dense.shape[1]).to(device)
	optimizer = torch.optim.Adam(model.parameters(), lr=AE_LR)
	criterion = nn.MSELoss()

	dataset = torch.utils.data.TensorDataset(
		torch.tensor(X_train_ae, dtype=torch.float32),
	)
	loader = DataLoader(dataset, batch_size=AE_BATCH_SIZE, shuffle=True)

	for epoch in range(1, AE_EPOCHS + 1):
		model.train()
		total_loss = 0.0
		total_examples = 0
		total_batches = len(loader)
		for batch_idx, (batch_x,) in enumerate(loader, start=1):
			batch_x = batch_x.to(device)
			optimizer.zero_grad()
			recon = model(batch_x)
			loss = criterion(recon, batch_x)
			loss.backward()
			optimizer.step()

			total_loss += loss.item() * batch_x.size(0)
			total_examples += batch_x.size(0)

			if batch_idx % PROGRESS_BATCH_EVERY == 0 or batch_idx == total_batches:
				print(
					f"  [Autoencoder] Batch {batch_idx}/{total_batches} | "
					f"Running MSE: {total_loss / max(total_examples, 1):.6f}"
				)

		epoch_loss = total_loss / max(total_examples, 1)
		print(f"[Autoencoder] Epoch {epoch}/{AE_EPOCHS} | Train MSE: {epoch_loss:.6f}")

	val_errors = reconstruction_errors(model, X_val_dense, device)
	threshold_candidates = np.quantile(val_errors, np.linspace(0.1, 0.95, 40))
	best_threshold = threshold_candidates[0]
	best_acc = -1.0

	for threshold in threshold_candidates:
		val_preds = (val_errors >= threshold).astype(int)
		acc = (val_preds == y_val).mean()
		if acc > best_acc:
			best_acc = acc
			best_threshold = threshold

	test_errors = reconstruction_errors(model, X_test_dense, device)
	test_preds = (test_errors >= best_threshold).astype(int)
	print(f"[Autoencoder] Validation threshold: {best_threshold:.8f} | Val Acc: {best_acc:.4f}")

	return test_preds


def ensure_output_dir(path: str):
	os.makedirs(path, exist_ok=True)


def join_output_path(output_dir: str, filename: str):
	return os.path.join(output_dir, filename)


def create_xgboost_model():
	try:
		from xgboost import XGBClassifier  # pylint: disable=import-outside-toplevel
	except ImportError as exc:
		raise ImportError(
			"XGBoost is required for this script. Install it with: pip install xgboost"
		) from exc

	return XGBClassifier(
		n_estimators=300,
		learning_rate=0.08,
		max_depth=8,
		subsample=0.9,
		colsample_bytree=0.9,
		objective="binary:logistic",
		eval_metric="logloss",
		random_state=SEED,
	)


def main():
	print("Starting training...")
	args = parse_args()
	validate_local_path(args.csv_path, "csv_path")
	validate_local_path(args.model_output, "model_output")
	validate_local_path(args.vocab_output, "vocab_output")
	validate_local_path(args.output_dir, "output_dir")

	set_seed(SEED)
	device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
	ensure_output_dir(args.output_dir)

	df = pd.read_csv(args.csv_path)
	df = df[[TEXT_COLUMN, LABEL_COLUMN]].dropna()
	# Convert to numeric if needed: status column has 0 (phishing) and 1 (safe)
	df[LABEL_COLUMN] = pd.to_numeric(df[LABEL_COLUMN], errors='coerce')
	df = df[df[LABEL_COLUMN].notna()].copy()
	df = df[df[LABEL_COLUMN].isin([0, 1])].copy()
	df["label"] = df[LABEL_COLUMN].astype(int)

	train_df, val_df, test_df = split_data(df)

	# Prefer using the repository `vocabletters.json` (character-level utf8 mapping).
	try:
		vocab = load_vocabletters(VOCABLETTERS_PATH)
		print(f"Loaded vocabletters from {VOCABLETTERS_PATH}")
	except Exception:
		print(f"Could not load {VOCABLETTERS_PATH}; falling back to automatic vocab build.")
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

	print(f"Using device: {device}")
	print(f"Train/Val/Test sizes: {len(train_dataset)}/{len(val_dataset)}/{len(test_dataset)}")
	print(f"Vocabulary size: {len(vocab)}")

	test_labels = np.array(test_df["label"].tolist())
	confusion_results = {}

	# Classical ML models trained on TF-IDF features.
	vectorizer = TfidfVectorizer(max_features=MAX_VOCAB_SIZE, ngram_range=(1, 2))
	X_train_tfidf = vectorizer.fit_transform(train_df[TEXT_COLUMN])
	X_val_tfidf = vectorizer.transform(val_df[TEXT_COLUMN])
	X_test_tfidf = vectorizer.transform(test_df[TEXT_COLUMN])

	y_train = train_df["label"].to_numpy()
	y_val = val_df["label"].to_numpy()

	classical_models = {
		"Decision Tree": DecisionTreeClassifier(random_state=SEED),
		"Random Forest": RandomForestClassifier(
			n_estimators=300,
			random_state=SEED,
			n_jobs=-1,
		),
		"XGBoost": create_xgboost_model(),
	}

	for model_name, model in classical_models.items():
		print(f"Training {model_name}...")
		print(f"[{model_name}] Fitting model on TF-IDF features...")
		model.fit(X_train_tfidf, y_train)
		print(f"[{model_name}] Predicting on test split...")
		preds = model.predict(X_test_tfidf)
		matrix = confusion_matrix(test_labels, preds, labels=[0, 1])
		confusion_results[model_name] = matrix.tolist()

	# Sequence models trained on token-id sequences.
	sequence_models = {
		"RNN": RNN,
		"LSTM": LSTM,
		"GRU": GRU,
	}
	gru_state = None

	for model_name, model_cls in sequence_models.items():
		print(f"Training {model_name}...")
		print(f"[{model_name}] Building model and moving to {device}...")
		model = model_cls(
			vocab_size=len(vocab),
			embed_dim=EMBED_DIM,
			hidden_dim=HIDDEN_DIM,
			output_dim=2,
			n_layers=N_LAYERS,
		).to(device)

		result = train_torch_classifier(
			model_name=model_name,
			model=model,
			train_loader=train_loader,
			val_loader=val_loader,
			test_loader=test_loader,
			device=device,
		)
		matrix = confusion_matrix(test_labels, result["test_preds"], labels=[0, 1])
		confusion_results[model_name] = matrix.tolist()

		if model_name == "GRU":
			gru_state = result["best_state"]

	# Autoencoder anomaly detector on TF-IDF vectors.
	print("Training Autoencoder...")
	X_train_dense = X_train_tfidf.toarray().astype(np.float32)
	X_val_dense = X_val_tfidf.toarray().astype(np.float32)
	X_test_dense = X_test_tfidf.toarray().astype(np.float32)

	auto_preds = train_autoencoder_and_predict(
		X_train_dense=X_train_dense,
		y_train=y_train,
		X_val_dense=X_val_dense,
		y_val=y_val,
		X_test_dense=X_test_dense,
		device=device,
	)
	auto_matrix = confusion_matrix(test_labels, auto_preds, labels=[0, 1])
	confusion_results["Autoencoder"] = auto_matrix.tolist()

	print("\nConfusion matrices on test split (rows=true, cols=pred):")
	for model_name, matrix in confusion_results.items():
		print(f"\n{model_name}")
		print(np.array(matrix))

	# Keep legacy output for downstream inference scripts expecting GRU + vocab files.
	local_model_path = "modelUrl.pt"
	local_vocab_path = "vocab.json"
	if gru_state is not None:
		torch.save(gru_state, local_model_path)
		save_output(local_model_path, args.model_output)
		print(f"GRU model saved to {args.model_output}")

	with open(local_vocab_path, "w", encoding="utf-8") as f:
		json.dump(vocab, f)
	save_output(local_vocab_path, args.vocab_output)
	print(f"Vocabulary saved to {args.vocab_output}")

	confusion_path = join_output_path(args.output_dir, "confusion_matrices.json")
	save_json_output(confusion_results, confusion_path)
	print(f"Confusion matrices saved to {confusion_path}")


if __name__ == "__main__":
	main()


