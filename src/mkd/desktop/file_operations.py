"""
File system operations for desktop automation.
"""
import os
import shutil
import subprocess
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import platform

logger = logging.getLogger(__name__)


class FileOperations:
    """
    Comprehensive file system operations for automation.
    
    Provides file and folder operations including:
    - File/folder creation, deletion, copying, moving
    - Opening files with specific applications
    - File system navigation
    - File properties and metadata
    - Batch operations
    """
    
    def __init__(self):
        """Initialize file operations."""
        self.platform = platform.system()
        
    def open_file(self, file_path: str, application: str = None) -> bool:
        """
        Open a file with default or specific application.
        
        Args:
            file_path: Path to the file
            application: Specific application to open with (optional)
            
        Returns:
            Success status
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File does not exist: {file_path}")
                return False
                
            if application:
                if self.platform == "Windows":
                    subprocess.run([application, str(path)], shell=True)
                elif self.platform == "Darwin":
                    subprocess.run(['open', '-a', application, str(path)])
                else:
                    subprocess.run([application, str(path)])
            else:
                if self.platform == "Windows":
                    os.startfile(str(path))
                elif self.platform == "Darwin":
                    subprocess.run(['open', str(path)])
                else:
                    subprocess.run(['xdg-open', str(path)])
                    
            return True
            
        except Exception as e:
            logger.error(f"Error opening file {file_path}: {e}")
            return False
            
    def open_folder(self, folder_path: str) -> bool:
        """
        Open a folder in the file explorer.
        
        Args:
            folder_path: Path to the folder
            
        Returns:
            Success status
        """
        try:
            path = Path(folder_path)
            if not path.exists():
                logger.error(f"Folder does not exist: {folder_path}")
                return False
                
            if self.platform == "Windows":
                subprocess.run(['explorer', str(path)])
            elif self.platform == "Darwin":
                subprocess.run(['open', str(path)])
            else:
                subprocess.run(['xdg-open', str(path)])
                
            return True
            
        except Exception as e:
            logger.error(f"Error opening folder {folder_path}: {e}")
            return False
            
    def create_file(self, file_path: str, content: str = "", overwrite: bool = False) -> bool:
        """
        Create a new file.
        
        Args:
            file_path: Path for the new file
            content: Initial content (optional)
            overwrite: Whether to overwrite if exists
            
        Returns:
            Success status
        """
        try:
            path = Path(file_path)
            
            if path.exists() and not overwrite:
                logger.error(f"File already exists: {file_path}")
                return False
                
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.info(f"Created file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating file {file_path}: {e}")
            return False
            
    def create_folder(self, folder_path: str) -> bool:
        """
        Create a new folder.
        
        Args:
            folder_path: Path for the new folder
            
        Returns:
            Success status
        """
        try:
            path = Path(folder_path)
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created folder: {folder_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating folder {folder_path}: {e}")
            return False
            
    def delete_file(self, file_path: str, confirm: bool = True) -> bool:
        """
        Delete a file.
        
        Args:
            file_path: Path to the file
            confirm: Whether to confirm before deletion
            
        Returns:
            Success status
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                logger.error(f"File does not exist: {file_path}")
                return False
                
            if confirm:
                # In a real implementation, you might want to show a dialog
                pass
                
            path.unlink()
            logger.info(f"Deleted file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False
            
    def delete_folder(self, folder_path: str, confirm: bool = True) -> bool:
        """
        Delete a folder and its contents.
        
        Args:
            folder_path: Path to the folder
            confirm: Whether to confirm before deletion
            
        Returns:
            Success status
        """
        try:
            path = Path(folder_path)
            
            if not path.exists():
                logger.error(f"Folder does not exist: {folder_path}")
                return False
                
            if confirm:
                # In a real implementation, you might want to show a dialog
                pass
                
            shutil.rmtree(path)
            logger.info(f"Deleted folder: {folder_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting folder {folder_path}: {e}")
            return False
            
    def copy_file(self, source: str, destination: str, overwrite: bool = False) -> bool:
        """
        Copy a file.
        
        Args:
            source: Source file path
            destination: Destination file path
            overwrite: Whether to overwrite if destination exists
            
        Returns:
            Success status
        """
        try:
            src_path = Path(source)
            dest_path = Path(destination)
            
            if not src_path.exists():
                logger.error(f"Source file does not exist: {source}")
                return False
                
            if dest_path.exists() and not overwrite:
                logger.error(f"Destination file already exists: {destination}")
                return False
                
            # Create parent directories if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src_path, dest_path)
            logger.info(f"Copied file: {source} -> {destination}")
            return True
            
        except Exception as e:
            logger.error(f"Error copying file {source} -> {destination}: {e}")
            return False
            
    def move_file(self, source: str, destination: str, overwrite: bool = False) -> bool:
        """
        Move/rename a file.
        
        Args:
            source: Source file path
            destination: Destination file path
            overwrite: Whether to overwrite if destination exists
            
        Returns:
            Success status
        """
        try:
            src_path = Path(source)
            dest_path = Path(destination)
            
            if not src_path.exists():
                logger.error(f"Source file does not exist: {source}")
                return False
                
            if dest_path.exists() and not overwrite:
                logger.error(f"Destination file already exists: {destination}")
                return False
                
            # Create parent directories if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(src_path), str(dest_path))
            logger.info(f"Moved file: {source} -> {destination}")
            return True
            
        except Exception as e:
            logger.error(f"Error moving file {source} -> {destination}: {e}")
            return False
            
    def copy_folder(self, source: str, destination: str, overwrite: bool = False) -> bool:
        """
        Copy a folder and its contents.
        
        Args:
            source: Source folder path
            destination: Destination folder path
            overwrite: Whether to overwrite if destination exists
            
        Returns:
            Success status
        """
        try:
            src_path = Path(source)
            dest_path = Path(destination)
            
            if not src_path.exists():
                logger.error(f"Source folder does not exist: {source}")
                return False
                
            if dest_path.exists():
                if not overwrite:
                    logger.error(f"Destination folder already exists: {destination}")
                    return False
                else:
                    shutil.rmtree(dest_path)
                    
            shutil.copytree(src_path, dest_path)
            logger.info(f"Copied folder: {source} -> {destination}")
            return True
            
        except Exception as e:
            logger.error(f"Error copying folder {source} -> {destination}: {e}")
            return False
            
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get file information and metadata.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                logger.error(f"File does not exist: {file_path}")
                return None
                
            stat = path.stat()
            
            info = {
                'name': path.name,
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'accessed': stat.st_atime,
                'is_file': path.is_file(),
                'is_directory': path.is_dir(),
                'extension': path.suffix,
                'parent': str(path.parent),
                'absolute_path': str(path.absolute())
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return None
            
    def list_directory(self, directory_path: str, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """
        List contents of a directory.
        
        Args:
            directory_path: Path to the directory
            include_hidden: Whether to include hidden files
            
        Returns:
            List of file/folder information dictionaries
        """
        try:
            path = Path(directory_path)
            
            if not path.exists() or not path.is_dir():
                logger.error(f"Directory does not exist: {directory_path}")
                return []
                
            items = []
            
            for item in path.iterdir():
                if not include_hidden and item.name.startswith('.'):
                    continue
                    
                try:
                    stat = item.stat()
                    item_info = {
                        'name': item.name,
                        'path': str(item),
                        'size': stat.st_size,
                        'created': stat.st_ctime,
                        'modified': stat.st_mtime,
                        'is_file': item.is_file(),
                        'is_directory': item.is_dir(),
                        'extension': item.suffix if item.is_file() else None
                    }
                    items.append(item_info)
                except:
                    # Skip items we can't access
                    pass
                    
            return items
            
        except Exception as e:
            logger.error(f"Error listing directory {directory_path}: {e}")
            return []
            
    def search_files(self, directory: str, pattern: str, recursive: bool = True) -> List[str]:
        """
        Search for files matching a pattern.
        
        Args:
            directory: Directory to search in
            pattern: File name pattern (glob pattern)
            recursive: Whether to search subdirectories
            
        Returns:
            List of matching file paths
        """
        try:
            path = Path(directory)
            
            if not path.exists() or not path.is_dir():
                logger.error(f"Directory does not exist: {directory}")
                return []
                
            if recursive:
                matches = list(path.rglob(pattern))
            else:
                matches = list(path.glob(pattern))
                
            return [str(match) for match in matches if match.is_file()]
            
        except Exception as e:
            logger.error(f"Error searching files in {directory}: {e}")
            return []
            
    def get_disk_usage(self, path: str) -> Optional[Dict[str, int]]:
        """
        Get disk usage information for a path.
        
        Args:
            path: Path to check
            
        Returns:
            Dictionary with total, used, and free space in bytes
        """
        try:
            usage = shutil.disk_usage(path)
            return {
                'total': usage.total,
                'used': usage.total - usage.free,
                'free': usage.free
            }
        except Exception as e:
            logger.error(f"Error getting disk usage for {path}: {e}")
            return None