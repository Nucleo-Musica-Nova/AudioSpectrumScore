# AudioSpectrumScore Converter

The AudioSpectrumScore Converter is a Python script that enables the creation of musical scores with the main partials from audio files in the `.wav`, `.aif`, and `.aiff` formats. It processes audio files in the same directory as the script, analyzes their partials, and generates a visual representation of these partials in a musical score.

## How to Use

To utilize this script, follow these simple steps:

Prerequisites: Make sure you have Python installed on your system.

Installation: In the directory containing the main.py script and the requirements.txt file, install the required Python packages by running the following command:

``` bash
python3 -m pip install -r requirements.txt
```

For Windows users, replace python3 with python.

Prepare Audio Files: Copy all the audio files that you want to analyze and convert into the same directory as the main.py script.

Run the Script: From the directory containing main.py, execute the script by running the following command:

``` bash
python3 main.py
```
Windows users should use python instead of python3.

## Output

The script will process each audio file, analyze its main partials, and create a visual representation of these partials in a musical score. The resulting scores will be saved as PNG files in a subfolder named "pictures."

Enjoy using the Sound-to-Score Converter!
