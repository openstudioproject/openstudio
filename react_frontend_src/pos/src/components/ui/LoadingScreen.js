import React from "react"

const LoadingScreen = ({message, children}) =>
    <div className="content-wrapper">
        <section className="content">
            <i className="fa fa-spinner fa-pulse fa-3x fa-fw"></i><br /><br />
            Loading... <br />
            {message}
        </section>
    </div>

export default LoadingScreen