"""
Package Builder

Multi-platform package creation system for distributable applications.
Supports native packages for macOS, Windows, and Linux with dependency management.
"""

import os
import sys
import shutil
import subprocess
import tempfile
import logging
import json
import zipfile
import tarfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import platform
import hashlib

logger = logging.getLogger(__name__)


class PackageType(Enum):
    """Package types for different platforms"""
    # Cross-platform
    PYTHON_WHEEL = "wheel"
    PYTHON_SDIST = "sdist"
    ZIP_ARCHIVE = "zip"
    TAR_ARCHIVE = "tar"
    
    # macOS
    MACOS_APP = "app"
    MACOS_DMG = "dmg"
    MACOS_PKG = "pkg"
    
    # Windows
    WINDOWS_EXE = "exe"
    WINDOWS_MSI = "msi"
    WINDOWS_PORTABLE = "portable"
    
    # Linux
    LINUX_DEB = "deb"
    LINUX_RPM = "rpm"
    LINUX_APPIMAGE = "appimage"
    LINUX_SNAP = "snap"


class CompressionType(Enum):
    """Compression types"""
    NONE = "none"
    GZIP = "gzip"
    BZIP2 = "bz2"
    XZ = "xz"
    ZIP = "zip"


@dataclass
class Dependency:
    """Package dependency specification"""
    name: str
    version: str = "*"
    source: str = "pypi"  # pypi, conda, system, url
    optional: bool = False
    platform_specific: Optional[str] = None
    architecture_specific: Optional[str] = None


@dataclass
class PackageMetadata:
    """Package metadata information"""
    name: str
    version: str
    description: str
    author: str = ""
    author_email: str = ""
    homepage: str = ""
    license: str = ""
    keywords: List[str] = field(default_factory=list)
    classifiers: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    entry_points: Dict[str, str] = field(default_factory=dict)


@dataclass
class PackageConfig:
    """Package building configuration"""
    package_type: PackageType
    metadata: PackageMetadata
    source_directory: str
    output_directory: str = "dist"
    
    # Build options
    include_dependencies: bool = True
    bundle_python: bool = False
    compression: CompressionType = CompressionType.GZIP
    exclude_patterns: List[str] = field(default_factory=lambda: ["*.pyc", "__pycache__", ".git"])
    include_patterns: List[str] = field(default_factory=list)
    
    # Platform-specific options
    macos_bundle_id: str = ""
    macos_codesign_identity: str = ""
    windows_icon: str = ""
    windows_console: bool = True
    linux_desktop_file: bool = True
    
    # Advanced options
    custom_build_script: str = ""
    post_build_commands: List[str] = field(default_factory=list)
    environment_variables: Dict[str, str] = field(default_factory=dict)


class PackageBuilder:
    """Multi-platform package builder"""
    
    def __init__(self, work_directory: str = None):
        self.work_directory = Path(work_directory or tempfile.mkdtemp())
        self.work_directory.mkdir(exist_ok=True)
        
        # Build tools
        self.build_tools = {
            PackageType.PYTHON_WHEEL: self._build_wheel,
            PackageType.PYTHON_SDIST: self._build_sdist,
            PackageType.ZIP_ARCHIVE: self._build_zip_archive,
            PackageType.TAR_ARCHIVE: self._build_tar_archive,
            PackageType.MACOS_APP: self._build_macos_app,
            PackageType.MACOS_DMG: self._build_macos_dmg,
            PackageType.WINDOWS_EXE: self._build_windows_exe,
            PackageType.WINDOWS_MSI: self._build_windows_msi,
            PackageType.LINUX_DEB: self._build_linux_deb,
            PackageType.LINUX_RPM: self._build_linux_rpm,
        }
        
        # Platform detection
        self.current_platform = self._detect_platform()
        
        # Build statistics
        self.build_stats = {
            "total_builds": 0,
            "successful_builds": 0,
            "failed_builds": 0,
            "build_history": []
        }
        
        logger.info(f"PackageBuilder initialized on {self.current_platform}")
    
    def _detect_platform(self) -> str:
        """Detect current platform"""
        system = platform.system().lower()
        if system == "darwin":
            return "macos"
        elif system == "windows":
            return "windows"
        elif system == "linux":
            return "linux"
        else:
            return "unknown"
    
    async def build_package(self, config: PackageConfig) -> Dict[str, Any]:
        """Build package according to configuration"""
        
        build_id = f"build_{len(self.build_stats['build_history'])}"
        start_time = time.time()
        
        build_result = {
            "build_id": build_id,
            "package_type": config.package_type.value,
            "start_time": start_time,
            "success": False,
            "output_files": [],
            "error_message": "",
            "build_log": []
        }
        
        try:
            logger.info(f"Starting package build: {config.metadata.name} ({config.package_type.value})")
            
            # Validate configuration
            if not await self._validate_config(config):
                raise ValueError("Package configuration validation failed")
            
            # Prepare build environment
            build_dir = await self._prepare_build_environment(config)
            
            # Execute build
            builder_function = self.build_tools.get(config.package_type)
            if not builder_function:
                raise NotImplementedError(f"Package type {config.package_type.value} not supported")
            
            output_files = await builder_function(config, build_dir)
            
            # Post-build processing
            processed_files = await self._post_build_processing(config, output_files)
            
            # Update result
            build_result["success"] = True
            build_result["output_files"] = processed_files
            
            logger.info(f"Package build completed successfully: {len(processed_files)} files created")
            
        except Exception as e:
            build_result["error_message"] = str(e)
            logger.error(f"Package build failed: {e}")
            
        finally:
            build_result["end_time"] = time.time()
            build_result["duration"] = build_result["end_time"] - start_time
            
            # Update statistics
            self._update_build_stats(build_result)
        
        return build_result
    
    async def _validate_config(self, config: PackageConfig) -> bool:
        """Validate package configuration"""
        
        # Check source directory exists
        source_path = Path(config.source_directory)
        if not source_path.exists():
            logger.error(f"Source directory not found: {config.source_directory}")
            return False
        
        # Check required metadata
        if not config.metadata.name:
            logger.error("Package name is required")
            return False
        
        if not config.metadata.version:
            logger.error("Package version is required")
            return False
        
        # Platform-specific validation
        if config.package_type in [PackageType.MACOS_APP, PackageType.MACOS_DMG]:
            if self.current_platform != "macos":
                logger.warning(f"Building {config.package_type.value} on {self.current_platform} may not work")
        
        elif config.package_type in [PackageType.WINDOWS_EXE, PackageType.WINDOWS_MSI]:
            if self.current_platform != "windows":
                logger.warning(f"Building {config.package_type.value} on {self.current_platform} may not work")
        
        elif config.package_type in [PackageType.LINUX_DEB, PackageType.LINUX_RPM]:
            if self.current_platform != "linux":
                logger.warning(f"Building {config.package_type.value} on {self.current_platform} may not work")
        
        return True
    
    async def _prepare_build_environment(self, config: PackageConfig) -> Path:
        """Prepare build environment"""
        
        # Create build directory
        build_dir = self.work_directory / f"build_{config.metadata.name}_{config.metadata.version}"
        if build_dir.exists():
            shutil.rmtree(build_dir)
        build_dir.mkdir(parents=True)
        
        # Copy source files
        source_path = Path(config.source_directory)
        dest_path = build_dir / "src"
        
        await self._copy_source_files(source_path, dest_path, config.exclude_patterns, config.include_patterns)
        
        # Create setup files if needed
        await self._create_setup_files(config, build_dir)
        
        # Set environment variables
        for key, value in config.environment_variables.items():
            os.environ[key] = value
        
        logger.debug(f"Build environment prepared: {build_dir}")
        return build_dir
    
    async def _copy_source_files(self, source: Path, dest: Path, exclude_patterns: List[str], 
                                include_patterns: List[str]) -> None:
        """Copy source files with filtering"""
        
        import fnmatch
        
        dest.mkdir(parents=True, exist_ok=True)
        
        for item in source.rglob("*"):
            if item.is_file():
                # Check exclusion patterns
                excluded = False
                for pattern in exclude_patterns:
                    if fnmatch.fnmatch(item.name, pattern) or fnmatch.fnmatch(str(item.relative_to(source)), pattern):
                        excluded = True
                        break
                
                # Check inclusion patterns (if specified)
                if include_patterns:
                    included = False
                    for pattern in include_patterns:
                        if fnmatch.fnmatch(item.name, pattern) or fnmatch.fnmatch(str(item.relative_to(source)), pattern):
                            included = True
                            break
                    if not included:
                        excluded = True
                
                if not excluded:
                    # Copy file maintaining directory structure
                    relative_path = item.relative_to(source)
                    dest_file = dest / relative_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_file)
    
    async def _create_setup_files(self, config: PackageConfig, build_dir: Path) -> None:
        """Create setup files for Python packages"""
        
        if config.package_type in [PackageType.PYTHON_WHEEL, PackageType.PYTHON_SDIST]:
            # Create setup.py
            setup_py_content = f'''
from setuptools import setup, find_packages

setup(
    name="{config.metadata.name}",
    version="{config.metadata.version}",
    description="{config.metadata.description}",
    author="{config.metadata.author}",
    author_email="{config.metadata.author_email}",
    url="{config.metadata.homepage}",
    license="{config.metadata.license}",
    packages=find_packages(),
    install_requires={config.metadata.requirements},
    entry_points={config.metadata.entry_points},
    keywords={config.metadata.keywords},
    classifiers={config.metadata.classifiers},
    python_requires=">=3.8",
)
'''
            setup_file = build_dir / "setup.py"
            setup_file.write_text(setup_py_content.strip())
            
            # Create pyproject.toml
            pyproject_content = f'''
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{config.metadata.name}"
version = "{config.metadata.version}"
description = "{config.metadata.description}"
authors = [{{name = "{config.metadata.author}", email = "{config.metadata.author_email}"}}]
license = {{text = "{config.metadata.license}"}}
requires-python = ">=3.8"
dependencies = {config.metadata.requirements}
keywords = {config.metadata.keywords}
classifiers = {config.metadata.classifiers}

[project.urls]
Homepage = "{config.metadata.homepage}"
'''
            pyproject_file = build_dir / "pyproject.toml"
            pyproject_file.write_text(pyproject_content.strip())
    
    async def _build_wheel(self, config: PackageConfig, build_dir: Path) -> List[str]:
        """Build Python wheel package"""
        
        output_files = []
        
        try:
            # Run build command
            cmd = [sys.executable, "-m", "build", "--wheel", "--outdir", config.output_directory]
            result = subprocess.run(cmd, cwd=build_dir, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Find created wheel file
                output_dir = Path(config.output_directory)
                for wheel_file in output_dir.glob("*.whl"):
                    output_files.append(str(wheel_file.absolute()))
            else:
                raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("Wheel build timed out after 300 seconds")
        
        return output_files
    
    async def _build_sdist(self, config: PackageConfig, build_dir: Path) -> List[str]:
        """Build Python source distribution"""
        
        output_files = []
        
        try:
            # Run build command
            cmd = [sys.executable, "-m", "build", "--sdist", "--outdir", config.output_directory]
            result = subprocess.run(cmd, cwd=build_dir, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Find created source dist file
                output_dir = Path(config.output_directory)
                for sdist_file in output_dir.glob("*.tar.gz"):
                    output_files.append(str(sdist_file.absolute()))
            else:
                raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("Source distribution build timed out after 300 seconds")
        
        return output_files
    
    async def _build_zip_archive(self, config: PackageConfig, build_dir: Path) -> List[str]:
        """Build ZIP archive"""
        
        output_dir = Path(config.output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        zip_filename = f"{config.metadata.name}-{config.metadata.version}.zip"
        zip_path = output_dir / zip_filename
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            source_dir = build_dir / "src"
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    arc_name = file_path.relative_to(source_dir)
                    zip_file.write(file_path, arc_name)
        
        return [str(zip_path.absolute())]
    
    async def _build_tar_archive(self, config: PackageConfig, build_dir: Path) -> List[str]:
        """Build TAR archive"""
        
        output_dir = Path(config.output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine compression
        if config.compression == CompressionType.GZIP:
            mode = "w:gz"
            extension = ".tar.gz"
        elif config.compression == CompressionType.BZIP2:
            mode = "w:bz2"
            extension = ".tar.bz2"
        elif config.compression == CompressionType.XZ:
            mode = "w:xz"
            extension = ".tar.xz"
        else:
            mode = "w"
            extension = ".tar"
        
        tar_filename = f"{config.metadata.name}-{config.metadata.version}{extension}"
        tar_path = output_dir / tar_filename
        
        with tarfile.open(tar_path, mode) as tar_file:
            source_dir = build_dir / "src"
            tar_file.add(source_dir, arcname=config.metadata.name)
        
        return [str(tar_path.absolute())]
    
    async def _build_macos_app(self, config: PackageConfig, build_dir: Path) -> List[str]:
        """Build macOS application bundle"""
        
        if self.current_platform != "macos":
            raise RuntimeError("macOS app bundles can only be built on macOS")
        
        try:
            # Use py2app or similar tool
            cmd = [
                sys.executable, "-m", "py2app",
                "--dist-dir", config.output_directory,
                "--alias" if config.bundle_python else "--standalone"
            ]
            
            if config.macos_bundle_id:
                cmd.extend(["--bundle-identifier", config.macos_bundle_id])
            
            # Add main script
            main_script = build_dir / "src" / "main.py"
            if main_script.exists():
                cmd.append(str(main_script))
            
            result = subprocess.run(cmd, cwd=build_dir, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                # Find created app bundle
                output_dir = Path(config.output_directory)
                app_bundles = list(output_dir.glob("*.app"))
                return [str(app.absolute()) for app in app_bundles]
            else:
                raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("macOS app build timed out after 600 seconds")
    
    async def _build_macos_dmg(self, config: PackageConfig, build_dir: Path) -> List[str]:
        """Build macOS DMG installer"""
        
        if self.current_platform != "macos":
            raise RuntimeError("DMG files can only be built on macOS")
        
        # First build the app bundle
        app_files = await self._build_macos_app(config, build_dir)
        
        if not app_files:
            raise RuntimeError("No app bundle created for DMG")
        
        app_path = Path(app_files[0])
        output_dir = Path(config.output_directory)
        dmg_path = output_dir / f"{config.metadata.name}-{config.metadata.version}.dmg"
        
        try:
            # Create DMG using hdiutil
            cmd = [
                "hdiutil", "create",
                "-volname", config.metadata.name,
                "-srcfolder", str(app_path),
                "-ov", "-format", "UDZO",
                str(dmg_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return [str(dmg_path.absolute())]
            else:
                raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("DMG build timed out after 300 seconds")
    
    async def _build_windows_exe(self, config: PackageConfig, build_dir: Path) -> List[str]:
        """Build Windows executable"""
        
        try:
            # Use PyInstaller
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--onefile" if not config.bundle_python else "--onedir",
                "--distpath", config.output_directory,
                "--workpath", str(build_dir / "build"),
                "--specpath", str(build_dir)
            ]
            
            if not config.windows_console:
                cmd.append("--windowed")
            
            if config.windows_icon:
                cmd.extend(["--icon", config.windows_icon])
            
            # Add main script
            main_script = build_dir / "src" / "main.py"
            if main_script.exists():
                cmd.append(str(main_script))
            
            result = subprocess.run(cmd, cwd=build_dir, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                # Find created executable
                output_dir = Path(config.output_directory)
                exe_files = list(output_dir.glob("*.exe"))
                return [str(exe.absolute()) for exe in exe_files]
            else:
                raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("Windows executable build timed out after 600 seconds")
    
    async def _build_windows_msi(self, config: PackageConfig, build_dir: Path) -> List[str]:
        """Build Windows MSI installer"""
        
        # First build the executable
        exe_files = await self._build_windows_exe(config, build_dir)
        
        if not exe_files:
            raise RuntimeError("No executable created for MSI")
        
        # Create MSI using cx_Freeze or similar
        # This is a placeholder - actual MSI creation would require more complex setup
        logger.warning("MSI creation not fully implemented - would use WiX toolset or similar")
        
        return exe_files  # Return exe for now
    
    async def _build_linux_deb(self, config: PackageConfig, build_dir: Path) -> List[str]:
        """Build Debian package"""
        
        if self.current_platform != "linux":
            logger.warning("Building DEB package on non-Linux platform")
        
        # Create debian package structure
        deb_dir = build_dir / "debian_package"
        deb_dir.mkdir(exist_ok=True)
        
        # DEBIAN control directory
        control_dir = deb_dir / "DEBIAN"
        control_dir.mkdir(exist_ok=True)
        
        # Create control file
        control_content = f'''Package: {config.metadata.name}
Version: {config.metadata.version}
Section: utils
Priority: optional
Architecture: all
Maintainer: {config.metadata.author} <{config.metadata.author_email}>
Description: {config.metadata.description}
'''
        
        (control_dir / "control").write_text(control_content)
        
        # Copy application files
        app_dir = deb_dir / "opt" / config.metadata.name
        app_dir.mkdir(parents=True, exist_ok=True)
        
        source_dir = build_dir / "src"
        shutil.copytree(source_dir, app_dir, dirs_exist_ok=True)
        
        # Build package
        output_dir = Path(config.output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        deb_filename = f"{config.metadata.name}_{config.metadata.version}_all.deb"
        deb_path = output_dir / deb_filename
        
        try:
            cmd = ["dpkg-deb", "--build", str(deb_dir), str(deb_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return [str(deb_path.absolute())]
            else:
                raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("DEB build timed out after 300 seconds")
        except FileNotFoundError:
            raise RuntimeError("dpkg-deb not found - install dpkg-dev package")
    
    async def _build_linux_rpm(self, config: PackageConfig, build_dir: Path) -> List[str]:
        """Build RPM package"""
        
        logger.warning("RPM package creation not fully implemented")
        
        # This would require creating RPM spec files and using rpmbuild
        # Placeholder implementation
        return []
    
    async def _post_build_processing(self, config: PackageConfig, output_files: List[str]) -> List[str]:
        """Post-build processing of output files"""
        
        processed_files = []
        
        for file_path in output_files:
            file_path_obj = Path(file_path)
            
            # Calculate checksums
            checksum_path = file_path_obj.with_suffix(file_path_obj.suffix + ".sha256")
            with open(file_path_obj, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            checksum_path.write_text(f"{file_hash}  {file_path_obj.name}")
            
            processed_files.append(file_path)
            processed_files.append(str(checksum_path))
            
            # Run post-build commands
            for command in config.post_build_commands:
                try:
                    # Replace placeholders
                    command = command.replace("{file}", str(file_path_obj))
                    command = command.replace("{name}", config.metadata.name)
                    command = command.replace("{version}", config.metadata.version)
                    
                    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
                    
                    if result.returncode != 0:
                        logger.warning(f"Post-build command failed: {command}")
                        
                except subprocess.TimeoutExpired:
                    logger.warning(f"Post-build command timed out: {command}")
        
        return processed_files
    
    def _update_build_stats(self, build_result: Dict[str, Any]) -> None:
        """Update build statistics"""
        
        self.build_stats["total_builds"] += 1
        
        if build_result["success"]:
            self.build_stats["successful_builds"] += 1
        else:
            self.build_stats["failed_builds"] += 1
        
        self.build_stats["build_history"].append({
            "build_id": build_result["build_id"],
            "package_type": build_result["package_type"],
            "success": build_result["success"],
            "duration": build_result.get("duration", 0),
            "timestamp": build_result["start_time"]
        })
        
        # Keep only last 100 builds
        if len(self.build_stats["build_history"]) > 100:
            self.build_stats["build_history"] = self.build_stats["build_history"][-100:]
    
    def get_build_statistics(self) -> Dict[str, Any]:
        """Get comprehensive build statistics"""
        
        success_rate = 0.0
        if self.build_stats["total_builds"] > 0:
            success_rate = (self.build_stats["successful_builds"] / self.build_stats["total_builds"]) * 100
        
        return {
            "total_builds": self.build_stats["total_builds"],
            "successful_builds": self.build_stats["successful_builds"],
            "failed_builds": self.build_stats["failed_builds"],
            "success_rate": success_rate,
            "supported_package_types": [pt.value for pt in PackageType],
            "current_platform": self.current_platform,
            "work_directory": str(self.work_directory),
            "recent_builds": self.build_stats["build_history"][-10:]
        }


# Utility functions for common build scenarios

def create_wheel_config(name: str, version: str, source_dir: str, **kwargs) -> PackageConfig:
    """Create configuration for Python wheel package"""
    
    metadata = PackageMetadata(
        name=name,
        version=version,
        description=kwargs.get("description", ""),
        author=kwargs.get("author", ""),
        author_email=kwargs.get("author_email", ""),
        homepage=kwargs.get("homepage", ""),
        license=kwargs.get("license", ""),
        requirements=kwargs.get("requirements", [])
    )
    
    return PackageConfig(
        package_type=PackageType.PYTHON_WHEEL,
        metadata=metadata,
        source_directory=source_dir,
        **{k: v for k, v in kwargs.items() if k not in metadata.__dict__}
    )


def create_executable_config(name: str, version: str, source_dir: str, **kwargs) -> PackageConfig:
    """Create configuration for platform-specific executable"""
    
    current_platform = platform.system().lower()
    
    if current_platform == "darwin":
        package_type = PackageType.MACOS_APP
    elif current_platform == "windows":
        package_type = PackageType.WINDOWS_EXE
    else:
        package_type = PackageType.LINUX_DEB
    
    metadata = PackageMetadata(
        name=name,
        version=version,
        description=kwargs.get("description", ""),
        author=kwargs.get("author", ""),
        author_email=kwargs.get("author_email", "")
    )
    
    return PackageConfig(
        package_type=package_type,
        metadata=metadata,
        source_directory=source_dir,
        bundle_python=kwargs.get("bundle_python", True),
        **{k: v for k, v in kwargs.items() if k not in ["bundle_python"] + list(metadata.__dict__.keys())}
    )