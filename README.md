# Android-SSL-unpinning

Simple python script which patches Android APK file to bypass SSL-pinning.

## Requirements

- Python3
- Java

## How to Run

```sh
python patch.py com.apk.file.to.patch.apk
# Patched APK file: com.apk.file.to.path.s.apk will be generated
```

## Good! But I got a problem :disappointed_relieved:

I am using an emulator called NoxPlayer, but I failed to install the patched apks.

So I try to sign to apk in a diffrerent way.

### Using jarsigner

#### Requirements

- JDK

#### Basic usage :neutral_face:

```sh
$ jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
-keystore cert/keys.jks -storepass 123456 target.apk repack \
-signedjar out.apk
```

#### Easy run :sunglasses:

```sh
$ python patch.py target.apk -j
```

## References

- [APKtool](https://ibotpeaches.github.io/Apktool/install/)
- [appium/sign](https://github.com/appium/sign)
