import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { v4 } from "uuid"
import { NavLink } from 'react-router-dom'
import { withRouter } from 'react-router'

import PageTemplate from "../../components/PageTemplate"
import Currency from "../../components/ui/Currency"
import CashbookTemplate from "./CashbookTemplateContainer"


class CashCountSet extends Component {
    constructor(props) {
        super(props)
        console.log("cash count set props:")
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        app: PropTypes.object,
    }

    componentWillMount() {
    }

    render() {
        const history = this.props.history
        const type = this.props.match.params.type


        return (
            <CashbookTemplate>
                <div className="box box-solid expenses-list"> 
                    <div className="box-header">
                        <h3 className="box-title">
                            Set {type} count
                        </h3>
                    </div>
                    <form onSubmit={() => this.onSubmit}>
                        <div className="box-body">
                            
                        
                        </div>
                        <div className="box-footer">
                            <button type="submit"
                                    className="btn btn-primary">
                                Save
                            </button>
                            <button type="button"
                                    className="btn btn-link"
                                    onClick={() => history.push('/cashbook')}>
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            </CashbookTemplate>
        )
    }
}

export default CashCountSet
