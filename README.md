# Logo Messenger
Logo Messenger is the official client of the Angelos project.

Logo comes from the greek word *Λόγῳ*, which means: reason, matter, statement, remark, saying, Word.

## Setup on macOS

We currently recommend to develop and to build Logo Messenger using Anaconda.

1. Clone the Logo repository.
   > git clone https://github.com/kristoffer-paulsson/logo.git
2. Position your self in the logo folder.
   > cd logo
3. Create a new conda environment with the Kivy package, and activate it.
   > conda create --name &lt;env&gt;
   >
   > conda activate &lt;env&gt;
   > 
   > conda install kivy -c conda-forge
 4. Initialize the project and install dependencies.
   > make init
 5. Build a windowed binary.
   > make
