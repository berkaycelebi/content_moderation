
import pickle
import torch
from nudenet import NudeDetector


# ---------------------------- Loading Models ---------------------------- #

# ------------------ Hate Speech ------------------- #

hate_model = pickle.load(
    open(r"hate_speech/saved_models/lr_model.pkl", "rb")
)  # path to hate speech model
hate_vect = pickle.load(
    open(r"hate_speech/saved_models/vectorizer.pkl", "rb")
)  # path to hate speech vectorizer

# ------------------ Spam Detection ------------------- #

spam_model = pickle.load(
    open(r"spam_classifier/saved_models/lr_model.pkl", "rb")
)  # path to spam model
spam_vect = pickle.load(
    open(r"spam_classifier/saved_models/vectorizer.pickle", "rb")
)  # path to spam vectorizer

# ------------------ Violence Detection ------------------- #

violence_model = pickle.load(
    open(r"violence_detection/saved_model/resnetmain.pkl", "rb")
)
checkpoint = torch.load(
    r"violence_detection/saved_model/main_model.pt",
    map_location=torch.device("cpu"),
)
violence_model.load_state_dict(checkpoint["state_dict"])

#  ---------------------------------------------------------------------- #

# initialize classifier (downloads the checkpoint file automatically the first time)
nudeDetector = NudeDetector()
