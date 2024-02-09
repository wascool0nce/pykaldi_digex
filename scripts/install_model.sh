file_path_fst="/app/models/model/HCLG.fst"
file_path_model="/app/models/model/final.mdl"


if [ ! -e "$file_path_fst" ]; then
    wget https://github.com/SergeyShk/Speech-to-Text-Russian/raw/master/model/HCLG.fst -P /app/models/model/

fi
if [ ! -e "$file_path_model" ]; then
    wget https://github.com/SergeyShk/Speech-to-Text-Russian/raw/master/model/final.mdl -P /app/models/model/
fi


cd app/models
python ./start_recognition.py


# Выводим сообщение об успешном завершении
echo "Done"

# Оставляем процесс в режиме ожидания (tail -f /dev/null) для того, чтобы контейнер не завершался
tail -f /dev/null