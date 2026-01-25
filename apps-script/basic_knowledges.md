### `const` | `var` | `let` 在javascript中的区别  
`var` 
1. **作用域**: `var` 在函数作用域内定义变量。如果在函数之外定义，则是全局作用域。`var` 不支持块级作用域。
2. **提升(Hoisting)**: `var` 声明的变量会被提升至作用域顶部，即在代码执行之前变量已存在（但未初始化）。
3. **可重声明**: 在同一作用域内可以多次使用 `var` 声明同一个变量。
4. **可重复赋值**: 将一个新值分配给已经声明的变量

```javascript 
function example() { 
  console.log(foo); // 输出: undefined 
  var foo = 'hello'; 
  console.log(foo); // 输出: 'hello' 
} 
``` 

`let`  
1. **作用域**: `let` 是块级作用域，即它所声明的变量只能在定义它的块中访问。 
2. **提升**: `let` 声明的变量也会被提升，但不会初始化。在变量定义之前访问它们会导致 `ReferenceError`。 
3. **不可重声明**: `let` 在同一作用域内不可重复声明同一个变量。
4. **可重复赋值**: 将一个新值分配给已经声明的变量

```javascript 
if (true) { 
  let bar = 'hi'; 
  console.log(bar); // 输出: 'hi' 
} 

// console.log(bar); // 这行代码会抛出 ReferenceError，因 bar 在块外不可用 
``` 

`const` 
1. **作用域**: 同 `let`，`const` 也是块级作用域。 
2. **常量声明**: `const` 用于声明常量。声明时需要进行初始化，且其绑定的变量引用不可更改（即对基本类型不可重新赋值，对复合类型如对象可修改其属性，但不可重新指向新对象）。 
3. **不可重声明**: `const` 在同一作用域内不可重复声明同一个变量。
4. **不可重复赋值**: 不允许对变量进行重复赋值。声明后，变量的值是不可变的（对于基本数据类型），引用类型的内容可变但引用自身不可重新赋值。 

```javascript 
const baz = 'world'; 
// baz = 'hello'; // 这行代码会导致 TypeError，因为常量不能被重新赋值 

const obj = { key: 'value' }; 
obj.key = 'new value'; // 合法操作，因为我们修改的是对象的属性 
// obj = {}; // 这行代码会导致 TypeError，因为我们试图重新分配一个新对象 
``` 

**其他声明变量的方法**  
除了 `var`、`let` 和 `const`，ES2015（ES6）之后没有新的内置变量声明方式。旧版本 JavaScript 使用 `var` 声明，而现代 JavaScript 开发基本只需使用 `let` 和 `const` 因为它们支持块级作用域和更明显的变量意图声明。  
#### 总结
- **var**: 更宽松，可以重复声明和赋值，但缺乏块级作用域，容易导致意外行为。 
- **let**: 提供块级作用域，无法重复声明，但可重复赋值，是一个灵活且常用的变量声明方式。 
- **const**: 提供块级作用域，不可重复声明或赋值（引用本身不可变，但对象属性和数组项可变），适用于声明不可变的变量。  

因此，`let` 和 `const` 的介绍更多集中在规范性和作用域控制上，而 `var` 是较为宽松的旧式方式，现代 JavaScript 编程更倾向于使用 `let` 和 `const` 来提高代码的可读性和可维护性。 

---

### `map` v.s. `forEach`  
Use `map` when you need to transform each element of an array and create a new array **with** the transformed values.  
```gs
function mapExample() { 
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet(); 
  var range = sheet.getRange("A1:A" + sheet.getLastRow()); 
  var values = range.getValues(); // This returns a 2D array 
  var doubledValues = values.map(function(row) { 
    return [row[0] * 2]; // Multiply the first (and only) element of each sub-array by 2 
  }); 

  // Assume we want to write the doubled values to the second column 
  sheet.getRange(1, 2, doubledValues.length, 1).setValues(doubledValues); 
} 
``` 

Use `forEach` when you need to perform operations on each element of an array **without** creating a new array.  
```gs
function forEachExample() { 
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet(); 
  var range = sheet.getRange("A1:A" + sheet.getLastRow()); 
  var values = range.getValues(); // This returns a 2D array 
  values.forEach(function(row) { 
    Logger.log(row[0]); // Log the first (and only) element of each sub-array 
  }); 
} 
``` 

---

In JavaScript, the three dots (...) represent the spread syntax  
```js
const originalArray = [1, 2, 3];
const copiedArray = [...originalArray]; // [1, 2, 3]

const originalObject = { a: 1, b: 2 };
const copiedObject = { ...originalObject }; // { a: 1, b: 2 }

const numbers = [1, 2];
const newNumbers = [...numbers, 3, 4]; // [1, 2, 3, 4]

function sum(a, b, c) {
    return a + b + c;
}
const args = [1, 2, 3];
const result = sum(...args); // 6
```

---

```js
var unique_member_list = [...new Set(member_list)] 是一个简洁地去除数组中重复值的方法：

new Set(member_list) 创建一个 Set 对象，Set 只存储唯一值
[...new Set(member_list)] 使用展开运算符将 Set 转回数组
这是 ES6 引入的一种简洁高效的数组去重方法。
```

---

```js
在JavaScript中，如果属性名（对象的键名）满足以下条件，可以不加引号：

以字母、下划线(_)或美元符号($)开头
后续字符可以是字母、数字、下划线或美元符号
不是JavaScript保留字(如if, class, return等)
```

---

```txt
在 Apps Script 里有两种函数
1.普通函数
  只能在 Apps Script 编辑器里运行
  或者被触发器（onEdit/onOpen/定时器）调用
  不会自动从表格里传参
  如果你直接点击“运行”，Apps Script 会：
    运行函数
    但不会给 a1Notation 传任何值
    所以 a1Notation 是 undefined
    getRange(undefined) 会报错
2.自定义函数（可以在表格里当公式用）
  在表格里用 =函数名() 调用
  只能在表格里调用
  Google Sheets 会自动把参数传进去
  不能修改表格（只读）
  不能读取格式/颜色（安全沙盒限制）
  不能访问 UI、触发器、外部 API
  不能写入单元格
  不能用 onEdit

  适合：
  做复杂计算（比普通公式更灵活）
  处理数组、对象、JSON（公式做不到）
  生成动态数组（比 ARRAYFORMULA 更自由）
  做 Google Sheets 公式做不到的字符串处理
  做跨表、跨文件的纯“读取”操作

  不适合：
  改颜色
  改格式
  改数据验证
  批量处理
  读取 RGB（因为自定义函数不能读颜色）
```

---

```txt
避免使用 ==, !=   因为他们会会自动进行类型转换，如
"1" == 1   → true
true == 1  → true
"" == 0    → true
"1" != 1   → false

永远使用：===，!==
```
