import os
import sys
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET
import subprocess as sp
import argparse as ap


def usage():
    print("Usage: python {} <APK file to patch>".format(sys.argv[0]))


def die(msg):
    print(msg)
    exit(1)


def check(proc):
    chk = True
    if os.name == "posix":  # Linux
        try:
            sp.check_call(["which", proc], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        except sp.CalledProcessError:
            chk = False
    else:  # Windows
        try:
            sp.check_call(["where", proc], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        except sp.CalledProcessError:
            chk = False

    return chk


def patch_manifest_file(manifest_file):
    tree = ET.parse(manifest_file)
    root = tree.getroot()

    application = root.find("application")
    network_security_config = application.get(
        "{http://schemas.android.com/apk/res/android}networkSecurityConfig"
    )

    # if network security config attribute not exists, inject it
    if network_security_config is None:
        application.set(
            "{http://schemas.android.com/apk/res/android}networkSecurityConfig",
            "@xml/network_security_config",
        )

    with open(manifest_file, "w", encoding="utf-8") as f:
        f.write(ET.tostring(root, encoding="utf-8").decode())


def patch_network_security_config(config_file):
    cfg = """<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <debug-overrides>
        <trust-anchors>
            <certificates src="user" />
        </trust-anchors>
    </debug-overrides>
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </base-config>
</network-security-config>
"""
    with open(config_file, "w") as f:
        f.write(cfg)


def main():

    check("java") or die("Java is not installed")

    if args.j:
        check("jarsigner") or die("jarsigner is not installed")

    apktool = "apktool.jar"
    sign = "sign.jar"
    target_apk = args.apk

    if not target_apk.endswith(".apk"):
        print(
            "The extension of `{}` is not .apk, is it really a APK file?".format(
                target_apk
            )
        )
        exit(1)

    target_apk_unpacked = target_apk.rstrip(".apk")
    target_apk_repacked = target_apk_unpacked + ".repack.apk"
    target_apk_signed = target_apk_unpacked + ".repack.s.apk"

    # Unpacking
    sp.run(["java", "-jar", apktool, "d", target_apk])

    # Patch security config of APK to trust user rook certificate
    manifest_file = Path(target_apk_unpacked) / "AndroidManifest.xml"
    patch_manifest_file(str(manifest_file))
    config_file = (
        Path(target_apk_unpacked)
        / "res"
        / "xml"
        / "network_security_config.xml"
    )
    patch_network_security_config(str(config_file))

    # Repacking
    sp.run(
        [
            "java",
            "-jar",
            apktool,
            "b",
            target_apk_unpacked,
            "-o",
            target_apk_repacked,
        ]
    )

    # Signing
    if args.j:
        sp.run(
            [
                "jarsigner",
                "-verbose",
                "-sigalg",
                "SHA256withRSA",
                "-digestalg",
                "SHA-256",
                "-keystore",
                "cert/keys.jks",
                "-storepass",
                "123456",  # This password is for cert/keys.jks
                target_apk_repacked,
                "repack",  # This is `alias` in cert/keys.jks
                "-signedjar",
                target_apk_signed,
            ]
        )
    else:
        sp.run(["java", "-jar", sign, target_apk_repacked])

    # Clean up
    shutil.rmtree(target_apk_unpacked)
    os.remove(target_apk_repacked)


if __name__ == "__main__":
    parser = ap.ArgumentParser()
    parser.add_argument("apk")
    parser.add_argument("-j", help="Use jarsigner", action="store_true")

    args = parser.parse_args()

    main()
