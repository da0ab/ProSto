# ProSto
Простой сборщик web проектов на **Python3**  требуются ``pip install sass csscompressor rjsmin watchdog``

- **ProSto.py** - следит за изменениями файлов в папке src
- **css.py** - собирает *css* ориентируясь на файлы c ``@import 'component-1/_component-1.scss';``
  - *ProSto.scss* -> **ProSto.css** -> **ProSto.min.css**
  - *ProStoCMS.scss* -> **ProStoCM.css** -> **ProStoCM.min.css**
- **js.py** - собирает все
  - *-init.js* -> **init.js**
  - *-vendor.js* -> **ProSto.min.js**
  - *-cms.js* -> **ProStoCMS.min.js**
- **html.py** - собирает **html** из *index-page.html* с простым набором переменных

```
@@include('components/html/_head.html',{
"lang":"ru",
"title":"Главная страница",
"description":"Описание проекта",
"keywords":"Ключи слова",
"copyright":"Автор",
"author":"Автор",
"url":"my_site.ru",
"robots": "all",
})

@@include('components/main/_main.html')
```
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
     ├── ProSto-CMS.scss
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

Для досборки под небольшие проекты есть небольшой хак:

Отдельный запуск **html.py** 

``python html.py my-site.ru`` 

создает
 - дубль *style.css* с именем *my-site.ru.css*
 - прописывает в *index-page.html* url, где требуется
   
```
 <meta property="og:image" content="https://my-site.ru/og-logo.png">
 <meta property="og:url" content="https://my-site.ru">
 <link rel="stylesheet" href="css/my-site.ru.css?v=0.0.1">
 <link href="https://my-site.ru/favicon.ico" sizes="any" rel="icon"> 
```
