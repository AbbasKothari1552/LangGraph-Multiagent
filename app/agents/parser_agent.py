import os

from app.state.main_graph_state import State

from app.tools.extractors.docs import extract_docx_text
from app.tools.extractors.excel import extract_excel_text
from app.tools.extractors.image import extract_image_text
from app.tools.extractors.pdf import extract_pdf_text

from app.core.logging_config import get_logger
logger = get_logger(__name__)

# Helper function
def get_extractor(filepath: str):
        """Get appropriate extractor based on file type"""
        # Split the path into root and extension
        _, ext = os.path.splitext(filepath)
        file_type = ext[1:].lower() if ext else ''  # Remove the dot

        if file_type == "pdf":
            return extract_pdf_text
        elif file_type in ["doc", "docx"]:
            return extract_docx_text
        elif file_type in ["xls", "xlsx"]:
            return extract_excel_text
        elif file_type in ["jpg", "jpeg", "png", "tiff"]:
            return extract_image_text
        return None



def parser_agent(state: State) -> State:
        """Main extraction method"""
        # logger.info(f"Starting text extraction for file_id: {file_id}")

        # get file path
        file_path = state.get("file_path")
        filename = state.get("file_name", "")
        if not filename:
            logger.error("No filename provided in state")
            state["extraction_status"] = "failed"
            return state
            
        filename = filename.split(".")[0] if "." in filename else filename
        file_dir = state.get("file_dir")
        output_dir = state.get("extracted_text_dir")

        # get extractor 
        extractor = get_extractor(file_path)
        if not extractor:
            logger.warning(f"No extractor available for file: {file_path}")
            state["extraction_status"] = "failed"
            return state
        
        try:
            input_path = file_path
            output_path = f"{output_dir}/{filename}.txt"
            result = extractor(
                input_path=input_path,
                output_path=output_path
            )

            # Update the existing state object instead of returning a new one
            state["doc_text"] = result.get("text")
            state["extraction_method"] = result.get("method")
            state["extracted_text_path"] = output_path
            state["extraction_status"] = "success"

            return state

        except Exception as e:
            logger.error(f"Extraction failed for {filename}: {str(e)}")

            state["extraction_status"] = "failed"
            return state

             


        
        # # Step 1: Retrieve FileMetadata
        # file_meta = self.db.query(FileMetadata).filter(FileMetadata.id == file_id).first()
        # if not file_meta:
        #     raise HTTPException(status_code=404, detail="File not found")
        
        # # Step 2: Check if already processed
        # existing_text_meta = self.db.query(TextMetaData).filter(TextMetaData.file_id == file_id).first()
        # if existing_text_meta and existing_text_meta.extraction_status == "completed":
        #     logger.info(f"Text already extracted for file_id: {file_id}")
        #     return existing_text_meta
            
        # extractor = self.get_extractor(file_meta.file_type)
        # if not extractor:
        #     logger.warning(f"No extractor available for file type: {file_meta.file_type}")
        #     file_meta.extraction_status = "failed"
        #     self.db.commit()
        #     return file_meta
        
        # try:
        #     # Step 4: Define output path
        #     content_filename = f"{file_meta.file_id}.txt"
        #     content_path = self.content_dir / content_filename

        #     input_path = BASE_PATH / Path(file_meta.upload_path)
            
        #     logger.info(f"Extracting content from: {file_meta.upload_path}")
        #     logger.info(f"Saving extracted content to: {content_path}")
            
        #     # Step 5: Perform extraction
        #     result = extractor(
        #         input_path=input_path,
        #         output_path=str(content_path)
        #     )
            
        #     # Step 6: Create or update TextMetaData
        #     if not existing_text_meta:
        #         text_meta = TextMetaData(
        #             file_id=file_id,
        #             text_filename = content_filename,
        #             upload_path = str(content_path),
        #             extraction_status="completed"
        #         )
        #         self.db.add(text_meta)
        #     else:
        #         text_meta = existing_text_meta
        #         text_meta.upload_path = content_filename
        #         text_meta.extraction_status = "completed"
                
        #     self.db.commit()
        #     self.db.refresh(text_meta)

        #     logger.info(f"Extraction and storage completed for file_id: {file_id}")
        #     return text_meta
            
        # except Exception as e:
        #     logger.error(f"Extraction failed for {file_meta.filename}: {str(e)}")
            
        #     self.db.rollback()

        #     # Update status to failed if metadata exists
        #     if existing_text_meta:
        #         existing_text_meta.extraction_status = "failed"
        #         self.db.commit()

        #     raise HTTPException(
        #         status_code=500,
        #         detail=f"Content extraction failed: {str(e)}"
        #     )