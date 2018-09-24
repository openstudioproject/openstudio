import React from "react"

const InputGroupSearch = ({placeholder, onChange=f=>f}) => 
    <div className="input-group">
        <span className="input-group-addon">
            <i className="fa fa-search"></i>
        </span>
        <input type="text"
               className="form-control"
               placeholder={placeholder} 
               onChange={onChange}
               ref={input => input && input.focus()} />
            {/* placeholder="Search..." /> */}
    </div>


export default InputGroupSearch