"""
ensures availability of mpxj .net library.
"""
import os # fix for pyrevit engine 2.7.x
import shutil
import pathlib
import zipfile

import requests

import utils


def check_if_lib_files_download_is_required(target_dir, file_list):
    existing_files = []
    print("INFO: check if mpxj lib download is required..")
    for node in target_dir.iterdir():
        if node.is_file():
            existing_files.append(node.name)
    required_count = len(file_list)
    found_count = 0
    for path in file_list:
        file_name = path.split("/")[-1]
        if file_name in existing_files:
            found_count += 1
    if found_count == required_count:
        print("INFO: ok, all required dlls are present")
        return False
    else:
        print("INFO:"
              " download required: not all dlls were found")
        return True


def check_repo_server_available(url):
    print("INFO: checking availability of server: {}".format(url))
    resp = requests.get(url)
    status = resp.status_code
    if not status == 200:
        utils.exit_on_error("unable to connect to server: {}".format(url))
        return False
    return True


def download_lib(url, target_path):
    print("INFO: attempting to download (~140MB): {}".format(url))
    response = requests.get(url)
    if response.status_code == 200:
        with open(str(target_path), mode="wb") as zip_file:
            zip_file.write(response.content)
    else:
        utils.exit_on_error("error_code: {} unable to download: {}".format(response.status_code, url))
    if not target_path.exists():
        utils.exit_on_error("download not successful - aborting. please retry later.")
    print("INFO: {} downloaded successfully to: {}".format(lib_zip_name, target_path))


def extract_zip_to(zip_path, target_dir, file_names=None):
    print("INFO: unzipping {}".format(zip_path))

    required_count = len(file_names)
    found_count = 0
    current = 0

    with zipfile.ZipFile(str(zip_path)) as zip_file:
        if not file_names:
            zip_file.extractall(path=str(target_dir))
        else:
            for entry in zip_file.namelist():
                if entry in file_names:
                    found_count += 1
                    current += 1
                    print("INFO: extracting {} of {}: {}".format(current, required_count, entry))
                    zip_file.extract(entry, str(target_dir))
            print("INFO: extracted: {}".format(found_count))

    if not net45_from_zip_dir.exists():
        utils.exit_on_error("unzipping not successful - aborting. please retry later.")


def transfer_lib_components(extracted_dir, target_dir):
    print("INFO: transferring required dlls:")
    for node in extracted_dir.iterdir():
        source = node
        target = target_dir
        print("INFO: copying: {}".format(str(source)))
        # print(str(source), str(target))
        # shutil.copy()
        shutil.move(str(source), str(target))


def remove_dir(target):
    for path in sorted(target.glob('**/*'), reverse=True):
        if not path.exists():
            continue
        path.chmod(0o666)
        if path.is_dir():
            path.rmdir()
        else:
            path.unlink()
    target.rmdir()


def clean_up_temp_files(temp_dir):
    print("INFO: cleaning up temp files: {}".format(temp_dir))
    remove_dir(temp_dir)


def run_bootstrap():
    if not unzip_dir.exists():
        unzip_dir.mkdir()
    download_required = check_if_lib_files_download_is_required(lib_target_dir_path, unzip_file_names)
    if download_required:
        server_available = check_repo_server_available(REPO_SERVER)
        if server_available:
            download_lib(URL, lib_target_zip_path)
            extract_zip_to(lib_target_zip_path, unzip_dir, unzip_file_names)
            transfer_lib_components(net45_from_zip_dir, lib_target_dir_path)
            clean_up_temp_files(unzip_dir)


unzip_file_names = (
    "mpxj/src.net/lib/net45/commons-collections4-4.4.dll",
    "mpxj/src.net/lib/net45/commons-io-2.11.0.dll",
    "mpxj/src.net/lib/net45/commons-lang3-3.10.dll",
    "mpxj/src.net/lib/net45/commons-logging-1.2.dll",
    "mpxj/src.net/lib/net45/commons-math3-3.6.1.dll",
    "mpxj/src.net/lib/net45/IKVM.AWT.WinForms.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.Beans.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.Charsets.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.Cldrdata.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.Corba.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.Core.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.Jdbc.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.Localedata.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.Management.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.Media.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.Misc.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.Naming.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.Nashorn.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.Remoting.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.Security.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.SwingAWT.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.Text.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.Tools.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.Util.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.XML.API.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.XML.Bind.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.XML.Crypto.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.XML.Parse.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.XML.Transform.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.XML.WebServices.dll",
    "mpxj/src.net/lib/net45/IKVM.OpenJDK.XML.XPath.dll",
    "mpxj/src.net/lib/net45/IKVM.Reflection.dll",
    "mpxj/src.net/lib/net45/IKVM.Runtime.dll",
    "mpxj/src.net/lib/net45/IKVM.Runtime.JNI.dll",
    "mpxj/src.net/lib/net45/ikvm-native-win32-x64.dll",
    "mpxj/src.net/lib/net45/ikvm-native-win32-x86.dll",
    "mpxj/src.net/lib/net45/jackcess-4.0.1.dll",
    "mpxj/src.net/lib/net45/jsoup-1.15.3.dll",
    "mpxj/src.net/lib/net45/junit.dll",
    "mpxj/src.net/lib/net45/log4j-api-2.17.2.dll",
    "mpxj/src.net/lib/net45/mpxj.dll",
    "mpxj/src.net/lib/net45/mpxj-for-csharp.dll",
    "mpxj/src.net/lib/net45/mpxj-for-vb.dll",
    "mpxj/src.net/lib/net45/mpxj-test.dll",
    "mpxj/src.net/lib/net45/MpxjUtilities.dll",
    "mpxj/src.net/lib/net45/poi-5.2.2.dll",
    "mpxj/src.net/lib/net45/rtfparserkit-1.16.0.dll",
    "mpxj/src.net/lib/net45/sqlite-jdbc-3.42.0.0.dll",
)

URL = "https://github.com/joniles/mpxj/releases/download/v12.7.0/mpxj-12.7.0.zip"
REPO_SERVER  = URL.rsplit("/", 6)[0]
lib_zip_name = URL.split("/")[-1]

THIS_SCRIPT = pathlib.Path(__file__)
repo_root_path = THIS_SCRIPT.parent.parent.parent
lib_target_dir_path = repo_root_path / "mpxj_dot_net.lib" / "src.net" / "lib" / "net45"
unzip_dir = lib_target_dir_path / "tmp"
lib_target_zip_path = unzip_dir / lib_zip_name
net45_from_zip_dir = unzip_dir / "mpxj" / "src.net" / "lib" / "net45"
