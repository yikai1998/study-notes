盒子模型 box model  
- 网页的布局 指将元素摆放到网页的不同位置
- 在网页中的每个元素都是一个矩形
- 布局得先设置大小
- 盒子的组成部分：
  - 内容区 content  
    在元素的最内部，用来容纳子元素
  - 边框 border
    盒子的边界，border-width, border-color, border-style  
    border可以简写，同时设置三个样式 `border: solid red 10px`
  - 内边距 padding  
    内容和边框之间的距离
  - box-sizing 用来指定盒子可见框
    ```
    box-sizing: border-box;
    width: 300px;
    height: 300px;
    padding: 20px;
    background-color: #bfa;
    border: 10px red solid;
    margin-top: 100px;
    margin-bottom: 100px;
    padding-top: 100px;
    margin: auto; /*水平垂直居中*/
    当子元素的大小超过了父元素的内容区时，子元素会overflow，如何处理呢？用overflow样式
      可选值：默认visible，hidden隐藏，scroll生成水平和垂直的滚动条，auto根据需要自动判定生成滚动条
    
    ```
```html
<!--小练习-->
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Document-2025-05-15</title>
    <style>
        .w1 {
            border: 2px black solid;
            color: red;
            height: 50px;
            background-color: pink;
            width: 400px;
            margin: auto;
            /*
            margin: auto; 对 <p> 元素不起作用的原因是 <p> 元素默认是块级元素（block-level element），但它的宽度是自动的（默认情况下宽度会根据内容自动调整），
            而 margin: auto; 通常用于水平居中块级元素时，需要元素的宽度是固定的（或者设置了宽度）。
            解决方法: 为了让 margin: auto; 起作用，你需要给 .w1 设置一个固定的宽度
            */
            text-align: center;  /*水平居中用text-align*/
            line-height: 50px;  /*将行高设置成和元素高度一样*/
        }
    </style>
</head>
<body>

    <p class="w1">
        今天去游泳，很开心。
    </p>

</body>
</html>
```
## 关于“居中”的总结  
方法1: `margin: 0 auto;`实现居中，原理是 利用盒子模型在水平布局时的等式（左右外边距+可见框宽度=包含块宽度），但也有缺点: 没法处理垂直居中，且居中的元素必须指定宽度  
方法2: 如下。原理: 左右偏移量+左右外边距+可见框的宽度=包含块的宽度；同理“上下”。也有缺点: 宽高必须写死
```html
<style>
    .box1 {
        width: 400px;
        height: 400px;
        border: 10px red solid;
        position: relative;
    }
    .box2 {
        width: 200px;
        height: 200px;
        background-color: yellow;
        position: absolute;
        top: 0;
        bottom: 0;
        left: 0;
        right: 0;
        margin: auto;
    }
</style>
```
方法3: 通过表格。如下。缺点：水平居中还是得用老办法。第二种可以根据文字的内容动态控制子元素的宽度居中，子元素的宽度变成自适应。但如果父元素不指定宽度则会丢失宽度  
```html
    .box1 {
        width: 400px;
        height: 400px;
        border: 10px red solid;
        display: table-cell;
        vertical-align: middle;
    }
    .box2 {
        width: 200px;
        height: 200px;
        background-color: yellow;
        margin: 0 auto;
    }
```
```html
<style>
    .box1 {
        width: 400px;
        height: 400px;
        border: 10px red solid;
        display: table-cell;
        vertical-align: middle;
        text-align: center;
    }
    .box2 {

        display: inline-block;
        background-color: yellow;
        margin: 0 auto;
    }
</style>
```
方法4: 弹性盒。最强大，没有以上局限性。如下
```html
<style>
    .box1 {
        width: 400px;
        height: 400px;
        border: 10px red solid;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .box2 {
        background-color: yellow;
    }
</style>
```
    
# 来源：《新手学html+css》-- 北京希望电子出版社  
## 背景
```txt
background-image: url(括号里填图片链接/地址); 必须同时设置高度和宽度
background-repeat: no-repeat; 绑定的图片只出现一次
background-repeat: repeat; 绑定的图片会重复出现，横向和纵向都会重复
background-repeat: repeat-x; 绑定的图片会重复出现，横向
background-repeat: repeat-y; 绑定的图片会重复出现，纵向
background-attachment: fixed; 图片不会随着页面的滚动而滚动(消失)
background-attachment: scroll; 图片会随着页面的滚动而滚动(消失)
background-position 只有在背景图片只有一个的时候才生效 即no-repeat top/center/bottom/left/center/right
```
```html
<style>
    .temp-div-1 {
    color: white;
    background-image: url(kakashi.jfif);
    width: 400px;
    height: 800px;
    background-repeat: repeat-x;
    }
</style>
<body>
    <div class="temp-div-1" c>
        测试背景图片
    </div>
</body>
```
```txt
综合声明background:
<style>
    .temp-div-1 {
    color: purple;
    background: url(kyubi.jfif) repeat;
    width: 1200px;
    height: 1000px;
    }
</style>
```
## 文本
```txt
color 文本颜色
letter-spacing 字符间距
line-height 行间距
text-align 文本对齐方式
text-decoration underline下划线 line-through删除线 overline上划线
text-indent 首行缩进
text-transform capitalize每个单词的首字母大写 uppercase lowercase
white-space normal按照浏览器默认展示 pre和nowrap效果是一样的，文本内容超出框架宽度也不会换行，除非遇到换行符
font-size 字体大小
font-family 字体风格
CSS的简写属性来同时设置多个字体相关属性    font: bold italic 40px 'KaiTi', sans-serif;
```
```html
    <table border="2">
        <tr>
            <td style="color: green; letter-spacing: 15px; text-decoration: line-through">庐山升龙霸</td>
            <td style="color: red; text-indent: 20px; width: 150px; font-size: 40px; font-family: 'KaiTi'">庐山百龙霸</td>
            <td style="line-height: 55px; width: 30px; text-align: right;">庐山千龙霸</td>
            <td style="text-transform: uppercase; white-space: nowrap; font-family: cursive;">Fuck a, Fuck b, Fuck c</td>
        </tr>
    </table>
```
## 边框  
```txt
border-color 边框颜色 可以针对四条边框 “上-右-下-左” 它需要与 border-width(xxx px) 和 border-style(solid dashed dotted double) 一起使用，才能正确显示边框
```
```html
<style>
    .temp-div-1 {
    color: purple;
    border-color: red green black blue;
    border-width: 10px;
    width: 80px;
    height: 130px;
    border-style: groove;
    }
</style>
<body>
    <div class="temp-div-1" >
        你好 上海
    </div>
</body>
```
## 边距  
```txt
外边距 margin-top margin-right margin-bottom margin-left margin(综合声明 按照“上-右-下-左”的顺序)
内边距 padding-top padding-right padding-bottom padding-left padding (padding 属性没有 auto 值)
```
```html
<style>
    .temp-div-1 {
    margin:100px auto;  <!-- 上下边距 左右边距 -->
    padding: 30px 40px 50px 90px;
    width: 400px;
    height: 100px;
    border-color: red;
    border-width: 5px;
    border-style: groove;
    }
</style>
<body>
    <div class="temp-div-1" >
        你好 上海
    </div>
</body>
```
## 列表
```txt
图片作为排序标签 list-style-image: url(path);
图案作为排序标签 list-style-type: disc/circle/square/decimal/lower-roman/lower-alpha/upper-latin/lower-greek/...
list-style-position outside/inside  排序标记是否显示在文本内容里
list-style 综合属性 list-style: url('kakashi.jfif') inside;
```
