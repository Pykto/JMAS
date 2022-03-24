# JMAS Graph Project

This project uses sensed data from the databases of the JMAS (Junta Municipal de Agua y Saneamiento) of Chihuahua, Chihuahua. The goal is to construct a water distribution network from multiple timestamps so they can be used as input for a classification method to identify an anomaly in the network. Likewise, the labels are generated using the database from the CIS (Centro de Información y Servicio), where users report malfunctions, low pression, or water shortage. These calls come from different zones, so six different sets of labels are generated to identify which one fits better the data. 

### Database Install

The JMAS databes (jmas1.backup) is hosted on [PostgreSQL](https://www.postgresql.org/download/). You can also download [pgadmin4](https://www.pgadmin.org/download/) for a more visual interface. 

Once installed, create the database with name jmas. It is important not to change the name of the database.

```
$ psql
$ CREATE DATABASE jmas WITH TWMPLATE template0;
$ \l
$ \q
```
Finally, use pg_restore to import the data.
```
$ pg_restore -d jmas –v “./<PATH>/jmas1.backup"
```
The data used in this experiments correspond to the following query:
```
SELECT datetime, valor, clave_inst
FROM base_ana
WHERE clave_inst = 
	Any(SELECT distinct(key) FROM base_instalation WHERE type = '2')
	AND LOWER(punto) LIKE LOWER('Nivel')
	AND valor >= 0
ORDER BY 
	datetime ASC,
	clave_inst ASC
```
The order in which the columns must not be changed either. The code will search for datetime, valor, and  clave_inst in that order. Also, the rows must be ordered by datetime, since the data separation is made  by hour.

### Python dependencies

(Optional) Before starting downloading packages, it is recommended using a virtual enviroment. In the path where you would like to save the project, one way you can create the virtual enviroment the following way:
```
python3 -m venv <NAME>
source ./<NAME>/bin/activate
```

To install the dependencies, you can use pip on the requirements.txt file. This will automatically install all needed packages.
```
pip3 install -r ./<PATH>/requirements.txt
```

### Running code

The first thing you need to do is the preprocessing phase. In the main directory, simply run the preprocessing.py. It will arrange the data, create necessary files, and generate the graphs. However, this does not output the final usable data.

You can generate the graphs by creating a matrix of DTW values or Correlation Coefficient. DTW is set to default.
```
python3 preprocessing.py --m dtw
python3 preprocessing.py --m corrcoef
```

After this, the labels and the graphs will be generated. Since there are six sets of labels, the range of dates of every set is different, so the data must be "aligned" so that every graph is paired with a label. To generate the datasets, simply run generate_dataset.py. 

The optional parameter --z correspond to the zone of which dataset will be generated. It goes from a rango of 1-6, and not adding the parameter will generate all datasets. That will output a "jmas_dataset_<ZONE>.pickle" file.
```
python3 generate_dataset.py --z 1
python3 generate_dataset.py --z 1 2 3
```

### (Optional) Classification

There's also a piece of code to do the embeddings and the classification. In case you do not wish to structure your own classification proccess, you can use the file provided in the repo.
```
python3 classify.py ./<PATH>/jmas_dataset_<ZONE>.pickle 
```

Parameter | Description | Options | Default
--- | --- | --- | ---
--c | Classifier | SVM, RF, DT, GNN | SVM 
--e | Epochs | Any integer | 100 
--emb | [Embedding Method](https://github.com/benedekrozemberczki/karateclub) | g2v, rg2v, sf| g2v
--d | Embedding Dimension | Any integer | 256
--k | k-value for RanGraph2Vec | Decimal number from range 0-1 | 0.75 



