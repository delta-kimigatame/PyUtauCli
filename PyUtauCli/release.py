import datetime
import shutil
import os
import os.path

PYPI_DIR = os.path.join("..", "release", "PYPI")
PYPI_TEST_DIR = os.path.join("..", "release", "PYPI_test")
PROJECTNAME = "PyUtauCli"


SOURCE_FILES = []
for pathname, dirnames, filenames in os.walk("."):
    if "env" in pathname:
        continue
    if "tests" in pathname:
        continue
    for filename in filenames:
        if not filename.endswith(".py"):
            continue
        if filename != "release.py" and filename != "tmp.py":
            SOURCE_FILES.append(os.path.join(pathname, filename))
            
print(SOURCE_FILES)
README=os.path.join("..","README.md")
LICENSE=os.path.join("..","LICENSE")


for file in SOURCE_FILES:
    os.makedirs(os.path.join(PYPI_TEST_DIR, "src", PROJECTNAME, os.path.dirname(file)), exist_ok=True)
    os.makedirs(os.path.join(PYPI_DIR, "src", PROJECTNAME, os.path.dirname(file)), exist_ok=True)
    with open(file, "r", encoding="utf-8") as fr:
        lines = fr.readlines()
    for i in range(len(lines)):
        if("import settings." in lines[i]):
            lines[i] = lines[i].replace("import settings.", "from ..settings import ")
        if("import common." in lines[i]):
            lines[i] = lines[i].replace("import common.", "from ..common import ")
        if("from voicebank" in lines[i]):
            lines[i] = lines[i].replace("from voicebank", "from ..voicebank")
        if("import settings\n" in lines[i]):
            lines[i] = lines[i].replace("import settings\n", "from .. import settings\n")
        if("import voicebank\n" in lines[i]):
            lines[i] = lines[i].replace("import voicebank\n", "from .. import voicebank\n")
    with open(os.path.join(PYPI_TEST_DIR, "src", PROJECTNAME, file), "w", encoding="utf-8") as fw:
        fw.write("".join(lines))
        
    shutil.copy(os.path.join(PYPI_TEST_DIR, "src", PROJECTNAME, file), os.path.join(PYPI_DIR, "src", PROJECTNAME, file))

with open(os.path.join(PYPI_DIR, "src", PROJECTNAME, "__init__.py"),"w") as fw:
    fw.write("")
with open(os.path.join(PYPI_TEST_DIR, "src", PROJECTNAME, "__init__.py"),"w") as fw:
    fw.write("")

    
if os.path.exists(LICENSE):
    shutil.copy(LICENSE, os.path.join(PYPI_TEST_DIR, "LICENSE"))
    shutil.copy(LICENSE, os.path.join(PYPI_DIR, "LICENSE"))
if os.path.exists(README):
    shutil.copy(README, os.path.join(PYPI_TEST_DIR, "README.md"))
    shutil.copy(README, os.path.join(PYPI_DIR, "README.md"))