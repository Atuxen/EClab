# EClab
This a codebase for reading EClab Biologic files and making plots

# For quick setup in Google colab

Explore and test this project directly in Google Colab with no setup required:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Atuxen/EClab.git/blob/main/notebook.ipynb)



# For local install
## If you do not have Python already, install it with Home Brew

### Home brew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
### Python

```bash
brew install python
```

## If you do have Python already, go directly here
### Clone repo
Clone the repository to your local folder:
```bash
git clone https://github.com/Atuxen/EClab.git
cd EClab

```

### Install libs and activate VE


#### Setup virtual environemnt and activate virtual environemnt
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Install packages in pyproject
```bash
pip install .
```



