from AIModelsTorch import GRU
import torch
import json
import re
from collections import defaultdict

MODEL_PATH = "model.pt"
VOCAB_PATH = "vocab.json"

MAX_SEQ_LEN = 200
EMBED_DIM = 128
HIDDEN_DIM = 128
N_LAYERS = 1

PAD_TOKEN = "<pad>"
UNK_TOKEN = "<unk>"

# Label mapping
LABEL_MAP_REVERSE = {0: "Safe Email", 1: "Phishing Email"}


def tokenize(text: str):
    return re.findall(r"[a-z0-9']+", str(text).lower())


def encode_text(text: str, vocab, max_len: int):
    token_ids = [vocab.get(token, vocab[UNK_TOKEN]) for token in tokenize(text)]
    token_ids = token_ids[:max_len]
    if len(token_ids) < max_len:
        token_ids += [vocab[PAD_TOKEN]] * (max_len - len(token_ids))
    return token_ids


def load_model_and_vocab(model_path: str, vocab_path: str, device):
    """Load saved model and vocabulary."""
    with open(vocab_path, 'r') as f:
        vocab = json.load(f)
    
    model = GRU(
        vocab_size=len(vocab),
        embed_dim=EMBED_DIM,
        hidden_dim=HIDDEN_DIM,
        output_dim=2,
        n_layers=N_LAYERS,
    ).to(device)
    
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    return model, vocab


def predict(email_text: str, model, vocab, device):
    """Predict whether an email is phishing or safe."""
    token_ids = encode_text(email_text, vocab, MAX_SEQ_LEN)
    input_tensor = torch.tensor([token_ids], dtype=torch.long).to(device)
    
    with torch.no_grad():
        logits = model(input_tensor)
        probabilities = torch.softmax(logits, dim=1)
        predicted_class = logits.argmax(dim=1).item()
        confidence = probabilities[0, predicted_class].item()
    
    label = LABEL_MAP_REVERSE[predicted_class]
    return label, confidence


def main():
    device = torch.device("cpu")
    
    # Load model and vocabulary
    print("Loading model and vocabulary...")
    model, vocab = load_model_and_vocab(MODEL_PATH, VOCAB_PATH, device)
    print(f"Model loaded from {MODEL_PATH}")
    print(f"Vocabulary loaded from {VOCAB_PATH} ({len(vocab)} tokens)")
    
    # Example usage
    sample_emails = [
        "Click here to verify your account immediately",
        "Meeting rescheduled to 3 PM tomorrow in conference room B",
        "Urgent: Update your password now or account will be locked",
        "Hej Sanne Corlin! Kan du kaste et blik det og vende tilbage til mig s==E5 hurtigt som muligt? -Olga",
        "Hello, I hope this email finds you well. I wanted to check in and see if you had any updates on the project we discussed last week. Please let me know if you need any additional information from my side. Best regards, John"
    ]
    
    print("\n" + "="*80)
    print("Making predictions on sample emails:")
    print("="*80 + "\n")
    
    for email in sample_emails:
        label, confidence = predict(email, model, vocab, device)
        print(f"Email: {email[:70]}...")
        print(f"Prediction: {label} (Confidence: {confidence:.2%})\n")


if __name__ == "__main__":
    main()
