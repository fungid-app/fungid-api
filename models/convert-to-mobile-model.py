import torch
from torch.utils.mobile_optimizer import optimize_for_mobile
from fastai.vision.all import *

name = "v0.4/mobilevitv2_175_384_in22ft1k-f4-fp16-bs1024-augs.pkl"
# orig = torch.load(name, map_location=torch.device('cpu'))

orig = load_learner(name, cpu=True)

final_model = torch.nn.Sequential(orig.model, torch.nn.Softmax()).to('cpu')

final_model.eval()
example = torch.rand(1, 3, 384, 384).cpu()
traced_script_module = torch.jit.trace(final_model, example)
traced_script_module_optimized = optimize_for_mobile(traced_script_module)
traced_script_module_optimized._save_for_lite_interpreter(
    "./mobile-image-model.pt"
)
