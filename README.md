# ViLaIn-TAMP
Development of Vision-Language Interpreter (ViLaIn) for Integrated Task and Motion Planning (TAMP).

## Installation
1. Install and create the conda environment:
```
conda create -n vilain-tamp python=3.10
conda activate vilain-tamp
```

2. Install dependencies:
```
cd ViLaIn-TAMP/
pip install -r requirements.txt
pip install -e .
```

## Set up OpenAI API key
Set your OpenAI API key in the environment variable (e.g. in ~/.bashrc or ~/.zshrc):
```
export OPENAI_API_KEY=<your_openai_api_key>
```

## Example Usage
Run an example PD generation by running the following command:
```
python scripts/test.py
```

## Project Structure

- `data`: offline datasets for PD generation
- `scripts`: standalone scripts for running PDDL generation with ViLaIn
- `vilain`: main implementation of ViLaIn



## Citations
```
@misc{shirai2023visionlanguage,
      title={Vision-Language Interpreter for Robot Task Planning}, 
      author={Keisuke Shirai and Cristian C. Beltran-Hernandez and Masashi Hamaya and Atsushi Hashimoto and Shohei Tanaka and Kento Kawaharazuka and Kazutoshi Tanaka and Yoshitaka Ushiku and Shinsuke Mori},
      year={2023},
      eprint={2311.00967},
      archivePrefix={arXiv},
      primaryClass={cs.RO}
}
```
