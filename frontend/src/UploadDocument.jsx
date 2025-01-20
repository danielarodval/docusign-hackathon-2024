import PropTypes from "prop-types"
import { Button } from "@/components/ui/button"

export default function UploadDocument({handleUploadDocument}){
    return(
        <>
            <Button onSubmit={handleUploadDocument}>Upload Documents</Button>
        </>
    )
}

UploadDocument.propTypes={
    handleUploadDocument : PropTypes.func
}