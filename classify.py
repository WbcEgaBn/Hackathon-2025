import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertModel, BertForSequenceClassification, AdamW
import torch.nn as nn
import torch.nn.functional as F
from sklearn.preprocessing import MultiLabelBinarizer

# Example dictionary entry
example_entry = {
    "title": "Liquor License Hearing",
    "description": "Review of new liquor license application",
    "longer_description": "The city council will discuss the approval of a new liquor license for a local bar.",
    "case_code": "LL-2025-01"
}

# Example topics
topics = ["Liquor License", "Public Safety", "Zoning", "Transportation", "Health"]

# Dummy dataset
data = [
    {"title": "Liquor License Hearing",
     "description": "Review of new liquor license application",
     "longer_description": "The city council will discuss the approval of a new liquor license for a local bar.",
     "case_code": "LL-2025-01",
     "labels": ["Liquor License"]},
    {"title": "Road Closure Notice",
     "description": "Temporary closure for road maintenance",
     "longer_description": "Maintenance on Main Street will require closure from 9AM to 5PM.",
     "case_code": "TR-2025-05",
     "labels": ["Transportation"]}
]

# Prepare labels
mlb = MultiLabelBinarizer(classes=topics)
all_labels = mlb.fit_transform([d["labels"] for d in data])

# Dataset class
class MeetingDataset(Dataset):
    def __init__(self, data, labels, tokenizer, max_length=128):
        self.data = data
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        # Combine all text fields
        text = f"{item['title']} [SEP] {item['description']} [SEP] {item['longer_description']} [SEP] {item['case_code']}"
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        input_ids = encoding['input_ids'].squeeze()
        attention_mask = encoding['attention_mask'].squeeze()
        labels = torch.tensor(self.labels[idx], dtype=torch.float)
        return input_ids, attention_mask, labels

# Initialize tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Create dataset and dataloader
dataset = MeetingDataset(data, all_labels, tokenizer)
dataloader = DataLoader(dataset, batch_size=2, shuffle=True)

# Define model
class BertMultiLabelClassifier(nn.Module):
    def __init__(self, n_labels):
        super(BertMultiLabelClassifier, self).__init__()
        self.bert = BertModel.from_pretrained('bert-base-uncased')
        self.dropout = nn.Dropout(0.3)
        self.classifier = nn.Linear(self.bert.config.hidden_size, n_labels)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        return logits

# Initialize model
model = BertMultiLabelClassifier(n_labels=len(topics))

# Loss and optimizer
criterion = nn.BCEWithLogitsLoss()
optimizer = AdamW(model.parameters(), lr=2e-5)

# Training loop (simple example)
for epoch in range(3):
    model.train()
    for input_ids, attention_mask, labels in dataloader:
        optimizer.zero_grad()
        outputs = model(input_ids, attention_mask)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
    print(f"Epoch {epoch+1} - Loss: {loss.item():.4f}")

# Prediction example
model.eval()
with torch.no_grad():
    text = f"{example_entry['title']} [SEP] {example_entry['description']} [SEP] {example_entry['longer_description']} [SEP] {example_entry['case_code']}"
    encoding = tokenizer(text, return_tensors='pt', truncation=True, padding='max_length', max_length=128)
    logits = model(encoding['input_ids'], encoding['attention_mask'])
    probs = torch.sigmoid(logits)
    predicted_labels = [topics[i] for i, p in enumerate(probs[0]) if p > 0.5]
    print("Predicted Topics:", predicted_labels)
