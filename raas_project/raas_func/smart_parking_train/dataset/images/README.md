# 📸 Image Dataset Information

## ⚠️ Custom Image Dataset Not Included in the Repository (Ignored via .gitignore)

This repository uses a custom **image dataset** created specifically for this project, consisting of **over 13,000 PNG images (~1.5 GB)**.  
To avoid exceeding GitHub's storage and performance limits, the dataset folder is **excluded from version control using `.gitignore`**.

As a result, the image files are **not tracked by Git** and are **not included in the repository**, but the code expects them to be present locally at the correct path.

You can **download the full dataset archive** from the **[Releases section](https://github.com/TheAndreyZakharov/Russian-Automotive-Assistance-System/releases)**.  
Look for the `images.zip` file under the **Assets** section of the latest release.

### 📥 How to Download
Go to:

```
Releases → Latest → Assets → images.zip
```

Then extract the archive to the correct local directory.

---

## 📁 Required File Location

After extracting the archive, make sure that **all PNG images are placed directly into the same folder where this `README.md` file is located**.  
This folder should contain **only the dataset images**, and no other files or subfolders.

---

## 🔧 File Paths Remain Valid

Although the image files themselves are not committed, **the paths used in the code remain unchanged**.  
Once you extract the dataset to the correct location, the training script:

```
raas_func/smart_parking_train/train_model.py
```

will work **without requiring any path modifications**.

---

<br><br><br><br><br>

---

# 📸 Информация о датасете изображений

## ⚠️ Собственный датасет изображений не включён в репозиторий (исключён через .gitignore)

Для этого проекта был создан собственный **датасет изображений**, содержащий **более 13 000 PNG-файлов (~1.5 ГБ)**.  
Чтобы избежать превышения ограничений GitHub по размеру и производительности, папка с изображениями **исключена из контроля версий с помощью `.gitignore`**.

Таким образом, сами изображения **не отслеживаются Git'ом** и **не включены в репозиторий**, но код всё ещё ожидает, что они будут находиться локально в нужной директории.

Вы можете **скачать полный архив изображений** в разделе **[Releases](https://github.com/TheAndreyZakharov/Russian-Automotive-Assistance-System/releases)**.  
Файл `images.zip` находится в разделе **Assets** последнего релиза.

### 📥 Как скачать
Перейдите:

```
Releases → Последний → Assets → images.zip
```

Затем распакуйте архив в нужную локальную папку.

---

## 📁 Расположение изображений

После распаковки архива убедитесь, что **все PNG-изображения находятся в той же папке, где расположен этот файл `README.md`**.  
В этой папке **не должно быть ничего, кроме изображений** — без дополнительных файлов или подкаталогов.

---

## 🔧 Пути к файлам остаются актуальными

Хотя сами изображения не коммитятся в репозиторий, **пути, используемые в коде, остаются прежними**.  
После распаковки архива скрипт обучения:

```
raas_func/smart_parking_train/train_model.py
```

будет работать **без необходимости менять пути**, если изображения находятся в правильной директории.

---
