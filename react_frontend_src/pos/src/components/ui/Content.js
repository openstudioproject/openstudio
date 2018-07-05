import React from "react"
import ContentHeader from './ContentHeader'

const Content = ({title, children}) =>
    <div className="content-wrapper">
        <section className="content">
            <ContentHeader title={title}>
                {children} 
            </ContentHeader>
        </section>
    </div>

export default Content