import React from "react"
import ContentHeader from './ContentHeader'

const initialStyle = {
    minHeight: window.innerHeight
}

const Content = ({title, children}) =>
    <div className="content-wrapper" style={initialStyle}>
        <section className="content">
            <ContentHeader title={title}>
                {children} 
            </ContentHeader>
        </section>
    </div>

export default Content