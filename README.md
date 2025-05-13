# ProSto
Простой сборщик web проектов на Python3

Структура проекта по умолчанию
```
ProSto.py
css.py
html.py
js.py
src
 ├── index-page.html
 └── components
     ├── ProSto.scss
     ├── ProStoCMS.scss
     └── component-1
         ├── _component-1.scss
         ├── _component-1-vendor.js
         ├── _component-1-cms.js
         ├── _component-1-init.js
         └── _component-1.html        
build
 ├── css
 │   ├── ProSto.css 
 │   ├── ProSto.min.css 
 │   ├── ProStoCMS.css 
 │   ├── ProStoCMS.min.css 
 │   └── style.css
 ├── js
 │   ├── ProSto.min.js 
 │   ├── ProStoCMS.min.js 
 │   └── init.js
 ├── fonts
 ├── images
 ├── favicons
 └── index-page.html
```
- **ProSto.py** - следит за изменениями файлов в папке src
- **css.py** - собирает *css* ориентируясь на файлы
  - *ProSto.scss*
    - ProSto.css
    - ProSto.min.css
  - *ProStoCMS.scss*
    - ProStoCMS.css
    - ProStoCMS.min.css
- **js.py** - собирает все
  - *-init.js* -> **init.js**
  - *-vendor.js* -> **ProSto.min.js**
  - *-cms.js* -> **ProStoCMS.min.js**
