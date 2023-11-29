### Text clustering
1. Concatenate day records into a single file
```
python3 concatenate_yesterday.py
```
2. Translate to English
```
cd translator
sh run.sh
cd ../
```
3. Split texts by sentences and save to pandas dataframe
```
sudo chmod -R 777 data/
python3 split_translations.py
```
4. Get embeddings
```
cd embeddings
sh run.sh
cd ../
```
5. Plot clusters
```
python3 clustering.py
```