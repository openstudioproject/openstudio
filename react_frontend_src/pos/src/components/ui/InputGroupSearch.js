import React from "react"

// const clear = () => {
//     const input = document.getElementById('InputSearch')
//     input.value = ''
//     const ev = new Event('input', { bubbles: true})
//     input.dispatchEvent(ev)
// }

const InputGroupSearch = ({placeholder, onChange=f=>f}) => 
    <div className="input-group">
        <span className="input-group-addon">
            <i className="fa fa-search"></i>
        </span>
        <input type="text"
               id="InputSearch"
               className="form-control"
               placeholder={placeholder} 
               onChange={onChange}
               ref={input => input && input.focus()} />
        {/* <span className="input-group-addon" onClick={clear}>
            <i className="fa fa-times"></i>
        </span> */}
    </div>


export default InputGroupSearch