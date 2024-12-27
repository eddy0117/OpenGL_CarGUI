## Symbolic link  Reference
> **Note：** You can refer to this symbolic link command to link your dataset source in the working directory. Reminder: The first parameter of the `ln` command is the dataset source, and the second is the path where the symbolic link will be created.


### nuscenes data Symbolic link :
```
ln -s /home/「username」/data_save/nuscenes  /home/ennis/dev/OpenGL_CarGUI/notebook/data/nuscenes 
```

### surroundocc data Symbolic link  :
```
ln -s /home/「username」/data_save/surroundocc /home/ennis/dev/OpenGL_CarGUI/notebook/data
```

---

### Folder structure
```
OpenGL_CarGUI/notebook
├── data
│   ├── nuscenes -> /home/username/data_save/nuscenes
│   └── surroundocc -> /home/username/data_save/surroundocc
├── extract_2dbbox.ipynb
├── generate_my_occ.ipynb
├── Image_process.ipynb
├── IPM.ipynb
└── json_process.ipynb
```