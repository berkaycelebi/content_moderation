
import pickle
import torch
from nudenet import NudeDetector


# ---------------------------- Loading Models ---------------------------- #

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
