import numpy as np
import os

class Accept:
    """Class for parsing and analyzing IBA myQA Accept measurement files."""
    
    def __init__(self, file_path):
        """Initialize the AcceptQA class by parsing the measurement file.

        Args:
            file_path (str): Path to the IBA ASCII measurement file.
        """

        file, ext = os.path.splitext(file_path)

        self.metadata: list[dict] = []
        self.data: list[np.ndarray] = []

        if ext == '.asc':
            self.parse_ascii_file(file_path)
        else:
            raise ValueError('Invalid file extension. Must be .asc')
    
    def get_dose_data(self):
        """Return the dose data for each measurement.

        Returns:
            list[np.ndarray]: List of numpy arrays containing the dose data for each measurement.
        """
        dose_data = []
        for data in self.data:
            dose_data.append(data[:, 3])
        return dose_data
    
    def get_position_data(self):
        """Return the position data for each measurement.

        Returns:
            list[np.ndarray]: List of numpy arrays containing the position data for each measurement.
        """
        position_data = []
        for data in self.data:
            position_data.append(data[:, 0:3])
        return position_data
    
    def parse_ascii_file(self, file_path):
        """Parse a IBA myQA Accept (6.0) ASCII measurement file and return metadata and data for each measurement.

        Args:
            file_path (str): Path to the IBA ASCII measurement file.
        
        Returns:
            metadata (list[dict]): List of dictionaries containing metadata for each measurement.
            data (list[np.ndarray]): List of numpy arrays containing the data for each measurement.
        """
        with open(file_path, 'r') as file:
            lines = file.readlines()

        metadata = []
        data = []
        current_metadata = {}
        current_data = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('# Measurement number'):
                if current_metadata:
                    metadata.append(current_metadata)
                    data.append(np.array(current_data))
                    current_metadata = {}
                    current_data = []
                current_metadata['measurement_number'] = int(line.split('\t')[-1])
            
            elif line.startswith('%'):
                parts = line[1:].split('\t', 1)
                if len(parts) == 2:
                    key, value = parts
                    current_metadata[key] = value.strip()
                else:
                    key = parts[0]
                    current_metadata[key] = None
            
            elif line.startswith(':') or line.startswith('#'):
                continue
            
            elif line.startswith('='):
                try:
                    current_data.append([float(val) for val in line.split('\t')[1:]])
                except ValueError:
                    continue

        if current_metadata:
            metadata.append(current_metadata)
            data.append(np.array(current_data))

        # Update metadata with STS and EDS values
        for entry in metadata:
            if 'FSZ' in entry:
                entry['FSZ'] = np.array([float(val) for val in entry['FSZ'].split('\t')[:2]])
            if 'STS ' in entry:
                sts_raw = entry['STS '].split('#')[0].strip()
                entry['STS'] = np.array([float(val) for val in sts_raw.split('\t')[:3]])
            if 'EDS ' in entry:
                eds_raw = entry['EDS '].split('#')[0].strip()
                entry['EDS'] = np.array([float(val) for val in eds_raw.split('\t')[:3]])

        self.metadata = metadata
        self.data = data
