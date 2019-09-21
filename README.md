# TuringArena

[![Join the chat at https://gitter.im/turingarena/turingarena](https://badges.gitter.im/turingarena/turingarena.svg)](https://gitter.im/turingarena/turingarena?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

*Create algorithmic challenges!*

[TuringArena](http://turingarena.org "TuringArena") is a toolkit and platform which allows to:

* define challenges which require an algorithmic solution;
* get/provide automatic evaluation of submitted solutions for an immidiate feedback to the problem recipient (student, class, employee/user/costumer to be trained/evaluated upon some competences), or for problem/system testing for the problem maker or proposer (teacher, trainer, advisor), or for student/team evaluation purposes;
* allow and organize the immediate use, the shared development, the publication and the promoting of the problem with possibly an eye to the respecting of the paternity and intellectual property of the problems that we fully recognize as forms of valuable content (we ourselves started this up as problem developers as part of our service for the italian olympiads in informatics and within our classes).

Some of the innovative features are:

* a language independent workflow, the problem designer is required a basic knowledge in just one programming language of its choice, and can always decide to which languages the evaluation service of solutions is open;
* virtually no restriction on the generality of challenges that can be represented;
* support for defining and implementing with minimum effort meaty problems from various fields (mainly in computer science and mathematics, but let's offer more concrete hints: algorithms, reductions between problems, computational complexity, games in a broad sense, mathematical programming, criptography, zero-knowledge proofs, programming tasks in specific languages or environments, workflows, ... and even support for problem solving without programming);  
* high levels of interactivity allowed and open ends for gamifications;
* an effective problem sharing approach which allows teachers and the like to organize in networks collaborating to the joint development of problem based didactive projects for the active learner and open source publishing the problems without neither spoiling them nor giving up their paternity, possibly even copyrighting them.


## Getting started

Here is how to use TuringArena on your local machine to develop and test challenges.

### Prerequisites

TuringArena is currently supported *only on Linux*, because we use
Linux-specific kernel interfaces to sandbox submissions and measure resource utilization. In case you have a different operating system we currently suggest you to install an Ubuntu 18.04 virtual machine, e.g. within Oracle VirtualBox (https://www.virtualbox.org/  https://www.oracle.com/it/virtualization/virtualbox/)

To use TuringArena on a local machine, the following tools are needed:
- `python3.6` or newer
- `pip`
- `gcc and g++` for compiling C/C++ submissions
- `libseccomp-dev` used for the submission sandbox
- `jq` used to format json output
- on Ubuntu/Debian, `python3-dev` for addictional header files 

Not required but recommended:
- `pipenv` to install in a virtual environment

You may also want the following optional dependencies:
- `openjdk-*-jdk` to run Java submissions
- `rustc` to run Rust submissions 

To install all of the required dependencies on Ubuntu 18.04:
```bash
sudo apt install python3.6 python3-pip build-essential jq libseccomp-dev
```
To install pipenv (we recommend its use):

```bash
sudo apt-get install python3-venv
```

### The main steps for installing TuringArena

1. Install the above dependencies.

2. Create the TuringArena base directory (see where you prefer within your file system):
```bash
mkdir turingarena
```

3. Enter in the TA base directory just created:
```bash
cd turingarena
```

4. Set up a virtual environment for TA (optional but recommended, see more below for the how and why)

5. Clone the turingarena repository.
   For this, go in the directory where you want to collocate the TuringArena base directory and enter:
```bash
git clone https://github.com/turingarena/turingarena.git
```
   If the download was successful (if you have git installed and network connection) you should now have a subdirectory named turingarena within your current directory (the TuringArena base directory also named turingarena)

6. Install TA (see more below for the how)

7. Also as a test, explore and experiment with the problems offered in the tutorial.

And rememer to offer us your feedback (or ask for our help) in case you encounter any problems with the installation.

### Unistall TuringArena (very clean if you used virtual environments)

If you used virtual environments as we suggested, just remove the TA base directory:
```bash
rm -rf turingarena
```
This will delete also its turingarena subdirectory where the core of the TA software is installed and the <code>venv_ta</code> subdirectory containing all softwares you have decided to install for experimenting or developing during your journey with that TA installation.

Apart for the installation of the prerequisites above (all anyhow useful and established, and well designed and robust softwares), it will all be back to the point when you first installed TurigArena if you opt to create a virtual environment in the TA base directory and use it whenever installing any further software relating with your TA experiences. Depending on the use you will make of TA, you might end up installing other softwares for the only purpouse of experimenting or working with TA. We suggest to install all these in the TA virtual environment.


### Setting Up a Virtual Environment

To create an environment for a project, after entering in the base directory for that project (e.g., the TA base directory in case of the TA project):

```bash
user@machine:~/.../turingarena$ python3 -m venv venv_ta
```
<p>With this command, you (user on your machine) are asking Python to create a virtual environment named <code>venv_ta</code>.
<p>After the command completes, the TA base directory has now a subdirectory named <em>venv_ta</em> where the virtual environment files are stored. Every software or library you are going to install for this environment (that is, when this environment is activated) will be stored here, without introducing conflicts with other versions of that same library in use by the global system on your machine or within other projects. Virtual environments are meant to prevent the breaking of dependencies you might have sometimes encountered. Already now, at its very creation, the directory <code>venv_ta</code> contains several packages which, at the beginning, provide just a copy of the global configuration at the time the environment was created.</p>

A common custome is to give a same name (usually <code>venv</code>) to each one of the virtual environments one creates. In this way, whenever you <code>cd</code> into a project, you know that the associated virtual environment, if any, is in the <code>venv</code> subfolder. If such a subfolder already exists then you know/remember that that project comes with its own environment already set up.
Moreover, you always know by heart the name of the virtual environment you need to activate each time you begin working on a project.
 We propose the <code>venv_ta</code> name that is short and explicit enough for that purpouse, because

1. a few solutions for the authomatic opening of the environments when you just enter in the project directory already exists (https://direnv.net/) (https://docs.pipenv.org/en/latest/advanced/) and you can give them a try in case you are in search for totally smooth workflows.

2. we envite our (more or less experienced) users to install under the <code>venv_ta</code> environment whatever other softwares they might end up using or experimenting in their explorations with TA.
Indeed, the isolation offered by virtual environments might actually help us in two ways: (1) preventing the disruption of the configuration of the python libraries on your machine, as it can be in use by other applications or projects, and (2) offering a common and uniform platform for collaborating with others on projects without paying any compatibility of versions nuisances toll. And the TuringArena project, in its broad vision, is much about collaborating with others.

<p>Note that in some operating systems you may need to use <code>python</code> instead of <code>python3</code> in the command above. Some installations use <code>python</code> for Python 2.x releases and <code>python3</code> for the 3.x releases, while others map <code>python</code> to the 3.x releases.
And there are many other possible differences and options for even more advanced uses of the environments, and these can change in time though environments and their use are here to stay. Also for these reasons, what you should get and appreciate here is more the aims and the why of environments. We suggest you to browse for some good introductory pages about python environments and their use. After this, try to put this knowlede into use to maintain all your future installations clean, also with other projects or when installing anything only to have a look or just a try at it. Be told this discipline will ultimately pay.</p>

#### Activating the environment (each time you want start acting on that project)

<p>You just finished some boring and nasty work and it is time for you to do something joyful and highly recreative. Why not to create a new TA problem or play a bit with TA?
You then go in the TA base directory, but, before starting, you need to activate the <code>venv_ta</code> virtual environment so that all dependencies will be there and, even if you end up installing and experimenting something new, this will not affect in any way the other installations and configurations on your machine.
 We assume that, regardless of the method you used to create it, you should now have your virtual environment created. To proceed, you have to tell the system that you want to use it, and you do that by <em>activating</em> it. This can be done by entering the following command from the TA base directory:</p>
<pre><code>$ source venv_ta/bin/activate
(venv) $ _
</code></pre>

As you can see, when you activate a virtual environment, the configuration of your terminal session is modified so that the Python interpreter stored inside it (in the directory <code>venv_ta</code>) is the one that is invoked when you type <code>python</code>. Also, the terminal prompt is modified to include the name of the activated virtual environment. The changes made to your terminal session are all temporary and private to that session, so they will not persist when you close the terminal window. If you work with multiple terminal windows open at the same time, it is perfectly fine to have different virtual environments activated on each one. (So you can keep up with your boring work meanwhile playing with TA.)</p>

### Installing/Updating TA

<p>We suggest you to do this after having created the <code>venv_ta</code> environment and from a terminal where you have it currenty activated. In any case, we assume you are in the TA base directory.
Also, either you have cloned already or clone now the TA repo with:

```bash
git clone https://github.com/turingarena/turingarena.git
```

If you are updating, you just enter the git directory turingarena (the subdirectory turingarena of the TA base directory turingarena) and pull down the new version with:

```bash
cd turingarena
git pull
cd ..
```
and in most cases when only updating it might actually be the case you do not need to act the following steps.

For sure you need to act them on a first intallation:</p>

#### Install / Upgrade
To install the TuringArena core, run the `setup.py` inside `src`. 
```bash
cd src/
python3 setup.py develop
cd ..
```

<p>If you want to confirm that your virtual environment now has TuringArena installed, you can start the Python interpreter and <em>import</em> the turingarena library into it:</p>
<pre><code class="python">&gt;&gt;&gt; import turingarena as ta
&gt;&gt;&gt; _
</code></pre>

<p>If this statement does not give you any errors you can congratulate yourself, as TuringArena is installed and ready to be used to create new problems and experiment with them in local.</p>

To install the TuringArena web interface, run the `setup.py` inside `taserver`.
```bash
cd taserver/
python3 setup.py develop
cd ..
```
With this interface you can offer to your community of problem solvers (if you are a teacher these might be your students), or pals, or customers to be trained, the experience of submitting their solutions via web, get it evaluated, and receive the rich feedback that TuringArena allows you to offer them at that point.

### Usage

To evaluate a solution, `cd` in the directory of the problem and run:
```bash
turingarena-dev evaluate path/to/solution.cpp
```

### First tests (running the example problems)

1. `cd` into any of the example problem directories.
   For example the one coming in this repo, with the TA core:
```bash
cd turingarena/examples/sum_of_two_numbers/
```
2. Evaluate a solution, say, `correct.cpp`:
```bash
turingarena-dev evaluate solutions/correct.cpp
```

