import React from "react"
import '../../../stylesheets/components/ui/LoadingScreen.scss'

const LoadingScreen = ({progress, message}) =>
    <div className="os_loader">
        <div className="os_loader_content">
            {/* <i className="fa fa-spinner fa-pulse fa-3x fa-fw"></i><br /><br /> */}
            Loading... {message}
            <div className="progress">
                <div className='progress-bar' style={{width: progress + '%'}}></div>
            </div>
        </div>
    </div>

export default LoadingScreen