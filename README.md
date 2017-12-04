# NLP

Mecab

[Mecab-ko(Download)](https://bitbucket.org/eunjeon/mecab-ko/downloads/)

```sh
tar zxvf mecab-0.996-ko-0.9.2.tar.gz
cd mecab-0.996-ko-0.9.2
./configure 
make
make check
sudo make install
```

[Mecab-ko-dic(Download)](https://bitbucket.org/eunjeon/mecab-ko-dic/downloads/)

```sh
tar zxvf mecab-ko-dic-2.0.3-20170922.tar.gz
cd mecab-ko-dic-2.0.3-20170922
./configure 
make
make check
sudo make install
```

`automake` Error:
```sh
./autogen.sh
```

`libmecab.so.2` Not Found:
```sh
sudo ldconfig
```

```sh
which mecab
/usr/local/bin/mecab

mecab -d /usr/local/lib/mecab/dic/mecab-ko-dic
```

