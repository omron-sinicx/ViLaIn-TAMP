# ViLaIn-TAMP
Development of Vision-Language Interpreter (ViLaIn) for Integrated Task and Motion Planning (TAMP).

## Project Structure

- `data`: domains, images, datasets
- `results`: generated problem descriptions
- `scripts`: standalone scripts for running PDDL generation with ViLaIn
- `src`: main implementation of ViLaIn
- `prompts`: prompt templates


## Installation

### SAM2
Install sam2 and download checkpoints & configs as follows:
```
git clone https://github.com/facebookresearch/sam2.git && cd sam2
pip install -e .
cd sam2
mkdir -p configs/sam2.1
wget https://github.com/facebookresearch/sam2/blob/main/sam2/configs/sam2.1/sam2.1_hiera_l.yaml -O configs/sam2.1/sam2.1_hiera_l.yaml
cd checkpoints
bash download_ckpts.sh
```


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
