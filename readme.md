# GEC

[Django文档](https://docs.djangoproject.com/zh-hans/3.0/)

[Vue.js文档](https://cn.vuejs.org/v2/guide/)

[@vue/cli文档](https://cli.vuejs.org/zh/guide/)

[项目结构参考文章](https://zhuanlan.zhihu.com/p/25080236)

[Element UI文档](https://element.eleme.cn/#/zh-CN/component/installation)

## 关于前端

- 前端使用`@vue/cli`构建，主要代码为`.vue`格式。其中，`src`文件夹下的`App.vue`文件为前端文件的入口，其它文件则通过在该文件中使用组件的方式进行导入；
- 我们所需编写的大部分代码都位于`./frontend/src/components`中，我们将会采用模块化的方案，将一个页面拆分为多个部分，在不同文件中进行编写，通过组件进行耦合；
- 我们通过在`main.js`中设置路由参数区分不同的页面，并在`App.vue`中访问该参数，从而得知我们应该渲染哪一个页面。这需要使用`vue-router`库，所以请在`frontend`目录下执行`yarn add vue-router`命令；
- 在每一个页面中，我们都会使用大量组件来拼接页面，通过在调用组件时传递参数，实现在同一个组件显示不同的值的效果。组件之间的调用请参照[组件基础](https://cn.vuejs.org/v2/guide/components.html)；
- 此外，还需要注意的一点是，在`<template></template>`标签内，只能有一个元素，因此需要先写一个`<div></div>`，然后再在里面实现具体的`HTML`代码；
- 为了界面的美观性，我们使用`Element UI`作为统一的UI框架，即提供UI的样式，如按钮、输入框、文本框等。`Element UI`的文档于上方给出；
- 在一个`.vue`文件中，我们需要实现的是：
  - 使用`HTML`实现基础的布局；
  - 使用`axios`来调用后端接口获取数据（后端接口目前未完成）；
  - 通过`Vue.js`来绑定数据，并响应按钮与数据变化；

## 一些关于SVN的注意事项

- SVN中，会**自动**应用所有的文件更改，所以，此时为了上传到云端，只需要执行`commit`操作即可
- 但是，在SVN中的所有文件增加和删除操作需要手动应用，即，如果新建了一个文件`test.txt`，那么我需要执行`svn add test.txt`（或者在软件中手动添加），才能确保其会被上传到云端
- 所以，在添加或删除文件时，要注意添加的确实是想要添加的文件。特别是诸如`./frontend/node_modules`这种文件夹，不要加到svn的版本控制里，因为其文件太多，会非常浪费svn同步文件的时间
- 使用时要记得经常update，确定当前自己的是最新版本
- 大家可以使用`svn status`操作来查看自己当前更改、添加或者删除的文件的状态

## 环境

- Mysql
- Python 3.7
- pip (记得换源)
  - Django 3.0.6
  - pymysql
  - markdown
- nodejs (>=10)
- npm (可能能用yarn完全替代)
  - @vue/cli (用于搭建环境，运行可能不需要)
- yarn (用于安装依赖和编译前端代码)(记得换源)

## 运行步骤

### 前端

在`frontend`目录下运行(只需要运行一次)：

```bash
yarn install
```

然后运行（每次编译前端代码时）：

```bash
yarn build
```

### 后端

在项目根目录运行

```bash
python manage.py runserver
```

## Tips

- 如果提示`django.core.exceptions.ImproperlyConfigured: mysqlclient 1.3.13 or newer is required; you have 0.9.3.`的话，可以到报错目录下更改源码，将报错源码删掉即可；或者更新自己的mysql和pymysql。
- Django中启用了自带的数据库管理界面，其路径为`http://[hostname]/admin`，用户名`super`，密码`superuser`。
- 由于前端采用了vue.js，所以前端每次更改后要重新编译才能生效，编译命令为`yarn build`，需要在`frontend`目录下执行。

## 项目目录结构

```

.
├── Miblog              //项目的Django配置文件
│   ├── __init__.py
│   ├── __pycache__
│   ├── asgi.py
│   ├── settings.py     //项目设置
│   ├── urls.py         //路由
│   └── wsgi.py
├── backend
│   ├── __init__.py
│   ├── __pycache__
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── frontend            //前端部分，为一个vue.js项目
│   ├── README.md
│   ├── babel.config.js
│   ├── dist            //编译生成的前端代码
│   ├── node_modules    //nodejs的package
│   ├── vue.config.js   //vuejs项目的配置
│   ├── package.json
│   ├── public
│   ├── src             //实际的代码
│   └── yarn.lock
├── manage.py
└── readme.md
```