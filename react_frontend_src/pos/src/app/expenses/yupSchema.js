import * as Yup from 'yup'

export const EXPENSE_SCHEMA = Yup.object().shape({
    amount: Yup.number()
      .required('This field is required'),
  })
