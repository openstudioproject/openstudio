import React from "react"
import '../../../stylesheets/components/ui/LoadingScreen.scss'

const LoadingScreen = ({message, children}) =>
    <div className="os_loader">
            <i className="fa fa-spinner fa-pulse fa-3x fa-fw"></i><br /><br />
            Loading... <br />
            {message}
    </div>

export default LoadingScreen