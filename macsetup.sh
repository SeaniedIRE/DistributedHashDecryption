xcode-select --install

usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

brew update

pip install --ignore-installed six

python -m pip install --user boto3

pip install virtualenv

git clone https://github.com/boto/boto3.git

mkdir  ~/.aws/credentials
mkdir  ~/.aws/config

$ git clone https://github.com/boto/boto3.git
$ cd boto3
$ virtualenv venv
...
$ . venv/bin/activate
$ pip install -r requirements.txt
$ pip install -e .
