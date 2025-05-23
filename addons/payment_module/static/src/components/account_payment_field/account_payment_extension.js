/** @odoo-module **/

import { patch } from '@web/core/utils/patch';
import { CharField } from '@web/views/fields/char/char_field'; // Nhập FieldChar từ module web

// Kế thừa và mở rộng FieldChar
patch(CharField.prototype, 'payment_module.CharFieldExtension', {
  setup() {
    this._super(); // Gọi setup() của component gốc
    console.log('FieldChar được mở rộng bởi payment_module!');
  },

  // Ghi đè phương thức onInput (xử lý khi người dùng nhập dữ liệu)
  onInput(ev) {
    console.log('onInput được mở rộng bởi payment_module!');
    this._super(ev); // Gọi phương thức gốc
    // Thêm logic tùy chỉnh
    const inputValue = ev.target.value;
    console.log(`Giá trị nhập vào: ${inputValue}`);
    if (inputValue.length > 5) {
      alert('Chuỗi bạn nhập đã vượt quá 5 ký tự!');
    }
  },

  // Thêm phương thức mới
  customMethod() {
    console.log('Đây là một phương thức tùy chỉnh từ payment_module!');
  },
});
