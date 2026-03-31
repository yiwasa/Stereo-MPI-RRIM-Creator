from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterBoolean)
import numpy as np
from osgeo import gdal

class CreateMPIRRIMAlgorithm(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    RADIUS = 'RADIUS'
    GAMMA_MPI = 'GAMMA_MPI'
    GAMMA_SLOPE = 'GAMMA_SLOPE'
    COLOR_MODE = 'COLOR_MODE'
    OUTPUT_TYPE = 'OUTPUT_TYPE'
    STEREO_EXAGGERATION = 'STEREO_EXAGGERATION'
    OUTPUT = 'OUTPUT'
    OUTPUT_RIGHT = 'OUTPUT_RIGHT'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CreateMPIRRIMAlgorithm()

    def name(self):
        return 'create_mpi_rrim'

    def displayName(self):
        return self.tr('Stereo MPI-RRIM Creator')

    def group(self):
        return ''

    def groupId(self):
        return ''

    def shortHelpString(self):
        return self.tr("""      
        <p>Please refer to <a href="https://github.com/yiwasa/Stereo-MPI-RRIM-Creator">the manual</a> for details.</p>
        <p>Recommend setting: Search radius of 150 m (for 5 m DEM: Search radius of 30 pixels). / Search radiusは150mがおすすめです（5m DEMの場合はSearch radius: 30）。</p>
        <p>To output anaglyph images or stereo pair images, please change the Stereo option. You can use the Stereo Image Viewer Plugin to view stereo images./ アナグリフ・ステレオペア画像の出力にはStereo optionを変更してください。Stereo Image Viewer Pluginを利用してステレオペア画像を表示できます。</p>
        <p></p>
        <p>References：Kaneda, H., & Chiba, T. (2019). <a href="https://pubs.geoscienceworld.org/ssa/bssa/article-abstract/109/1/99/567965/Stereopaired-Morphometric-Protection-Index-Red?redirectedFrom=fulltext">doi: 10.1785/0120180166</a> / <a href="https://civil.r.chuo-u.ac.jp/lab/geology/5_mrrim/mrrim.html">Stereo MPI-RRIMs Calculator</a></p>
        """)

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT, self.tr('Input DEM')))
        self.addParameter(QgsProcessingParameterNumber(self.RADIUS, self.tr('Search radius (pix)'), type=QgsProcessingParameterNumber.Integer, defaultValue=30, minValue=1))
        self.addParameter(QgsProcessingParameterNumber(self.GAMMA_MPI, self.tr('Gamma (MPI)'), type=QgsProcessingParameterNumber.Double, defaultValue=1.0, minValue=0.1))
        self.addParameter(QgsProcessingParameterNumber(self.GAMMA_SLOPE, self.tr('Gamma (slope)'), type=QgsProcessingParameterNumber.Double, defaultValue=0.8, minValue=0.1))
        self.addParameter(QgsProcessingParameterEnum(self.COLOR_MODE, self.tr('Color mode'), options=['MPI-RRIM (Slope:red, MPI:Cyan)', 'Blue (Slope:red, MPI:Cyan)'], defaultValue=0))
        self.addParameter(QgsProcessingParameterEnum(self.OUTPUT_TYPE, self.tr('Stereo option'), options=['Normal (2D)', 'Anaglyph', 'Stereopaired (parallel viewing)', 'Stereopaired (cross-eyed viewing)'], defaultValue=0))
        self.addParameter(QgsProcessingParameterNumber(self.STEREO_EXAGGERATION, self.tr('Vertical exaggeration (Try 1)'), type=QgsProcessingParameterNumber.Double, defaultValue=1.0, minValue=0.1))
        
        self.addParameter(QgsProcessingParameterBoolean('HIGH_RES_STEREO', self.tr('Increased (triple) resolution option'), defaultValue=False))
        
        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT, self.tr('Output Image (Main / Left)')))
        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT_RIGHT, self.tr('Output Image (Right: generated only for stereo images)'), optional=True))

    def processAlgorithm(self, parameters, context, feedback):
        input_layer = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        radius = self.parameterAsInt(parameters, self.RADIUS, context)
        gamma_mpi = self.parameterAsDouble(parameters, self.GAMMA_MPI, context)
        gamma_slope = self.parameterAsDouble(parameters, self.GAMMA_SLOPE, context)
        color_mode = self.parameterAsEnum(parameters, self.COLOR_MODE, context)
        output_type = self.parameterAsEnum(parameters, self.OUTPUT_TYPE, context)
        exaggeration = self.parameterAsDouble(parameters, self.STEREO_EXAGGERATION, context)
        high_res_stereo = self.parameterAsBool(parameters, 'HIGH_RES_STEREO', context)
        
        output_file = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        output_right_file = self.parameterAsOutputLayer(parameters, self.OUTPUT_RIGHT, context)

        input_path = input_layer.source()
        ds = gdal.Open(input_path)
        band = ds.GetRasterBand(1)
        no_data = band.GetNoDataValue()
        dem = band.ReadAsArray().astype(np.float32)

        if no_data is not None:
            dem[dem == no_data] = np.nan

        rows, cols = dem.shape
        gt = ds.GetGeoTransform()
        dx, dy = abs(gt[1]), abs(gt[5])

        # ★ 修正ポイント：計算前にDEM自体を3倍にリサンプリング
        if high_res_stereo:
            feedback.setProgressText("Increased (triple) resolution option in progress...")
            from scipy.ndimage import zoom
            
            # DEMをバイリニア補間(order=1)で3倍に拡大
            dem = zoom(dem, 3, order=1)
            rows, cols = dem.shape
            
            # 解像度が3倍になったので、ピクセルサイズ（dx, dy）は 1/3 になる
            dx = dx / 3.0
            dy = dy / 3.0
            
            # 入力された探索半径（ピクセル数）も3倍にしないと、実距離が短くなってしまうため補正
            radius = radius * 3
            
            # GeoTransform（ピクセルサイズと座標）を1/3スケールに更新
            new_gt = list(gt)
            new_gt[1] = gt[1] / 3.0
            new_gt[2] = gt[2] / 3.0
            new_gt[4] = gt[4] / 3.0
            new_gt[5] = gt[5] / 3.0
            gt = tuple(new_gt)

        feedback.setProgressText("1/3: Calculating Slope...")
        dy_grad, dx_grad = np.gradient(dem, dy, dx)
        slope = np.arctan(np.sqrt(dx_grad**2 + dy_grad**2))

        slope_max_fixed = 1.5708
        v_slope = np.clip(slope / slope_max_fixed, 0.0, 1.0) ** gamma_slope

        feedback.setProgressText("2/3: Calculating MPI...")
        mpi = np.zeros((rows, cols), dtype=np.float32)

        directions = [(0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1)]

        for i, (dy_dir, dx_dir) in enumerate(directions):
            if feedback.isCanceled(): return {}
            feedback.setProgress(int((i / 8.0) * 50))

            max_tangent = np.zeros((rows, cols), dtype=np.float32)
            dist_unit = np.sqrt((dx_dir * dx)**2 + (dy_dir * dy)**2)

            for r in range(1, radius + 1):
                y_shift, x_shift = dy_dir * r, dx_dir * r
                ys_src, ye_src = max(0, -y_shift), min(rows, rows - y_shift)
                xs_src, xe_src = max(0, -x_shift), min(cols, cols - x_shift)
                ys_dst, ye_dst = max(0, y_shift), min(rows, rows + y_shift)
                xs_dst, xe_dst = max(0, x_shift), min(cols, cols + x_shift)
                
                if ys_src >= ye_src or xs_src >= xe_src: break
                    
                dem_center = dem[ys_dst:ye_dst, xs_dst:xe_dst]
                dem_offset = dem[ys_src:ye_src, xs_src:xe_src]
                dz = dem_offset - dem_center
                dz /= (r * dist_unit)
                np.maximum(max_tangent[ys_dst:ye_dst, xs_dst:xe_dst], dz, out=max_tangent[ys_dst:ye_dst, xs_dst:xe_dst])
            
            mpi += np.arctan(max_tangent)

        mpi /= 8.0

        mpi_max_fixed = 1.0 
        v_mpi = np.clip(mpi / mpi_max_fixed, 0.0, 1.0) ** gamma_mpi
        v_mpi = np.clip(v_mpi * 1.5, 0.0, 1.0)

        feedback.setProgressText("3/3: Synthesizing RGB Image...")
        feedback.setProgress(80)

        if color_mode == 0:
            v_slope_color = np.clip(v_slope * 1.3, 0.0, 1.0)
            R_slope = 255.0 * (1.0 - v_slope * 0.1)
            G_slope = 255.0 * (1.0 - v_slope_color)
            B_slope = 255.0 * (1.0 - v_slope_color)
            mpi_weight = np.clip(v_mpi / 1.0, 0.0, 1.0)
            R_mpi = 255.0 * (1.0 - mpi_weight) + 18.0 * mpi_weight
            G_mpi = 255.0 * (1.0 - mpi_weight) + 112.0 * mpi_weight
            B_mpi = 255.0 * (1.0 - mpi_weight) + 121.0 * mpi_weight
            R = (R_slope * R_mpi) / 255.0
            G = (G_slope * G_mpi) / 255.0
            B = (B_slope * B_mpi) / 255.0
        else:
            v_slope_color = np.clip(v_slope * 1.3, 0.0, 1.0)
            R_slope = 255.0 * (1.0 - v_slope_color)
            G_slope = 255.0 * (1.0 - v_slope_color)
            B_slope = 255.0 * (1.0 - v_slope_color)
            mpi_weight = np.clip(v_mpi / 1.0, 0.0, 1.0)
            R_mpi = 255.0 * (1.0 - mpi_weight) + 18.0 * mpi_weight
            G_mpi = 255.0 * (1.0 - mpi_weight) + 112.0 * mpi_weight
            B_mpi = 255.0 * (1.0 - mpi_weight) + 121.0 * mpi_weight
            R = (R_slope * R_mpi) / 255.0
            G = (G_slope * G_mpi) / 255.0
            B = (B_slope * B_mpi) / 255.0

        R = np.clip(R, 0, 255).astype(np.uint8)
        G = np.clip(G, 0, 255).astype(np.uint8)
        B = np.clip(B, 0, 255).astype(np.uint8)

        R[np.isnan(dem)] = 255
        G[np.isnan(dem)] = 255
        B[np.isnan(dem)] = 255

        def save_tiff(filepath, r_arr, g_arr, b_arr, r_shape, c_shape, geo_t, trim_px):
            trim = trim_px
            if r_shape <= 2 * trim or c_shape <= 2 * trim:
                trim = 0
            if trim > 0:
                out_r = r_arr[trim:r_shape-trim, trim:c_shape-trim]
                out_g = g_arr[trim:r_shape-trim, trim:c_shape-trim]
                out_b = b_arr[trim:r_shape-trim, trim:c_shape-trim]
                out_rows = r_shape - 2 * trim
                out_cols = c_shape - 2 * trim
                new_gt = list(geo_t)
                new_gt[0] = geo_t[0] + trim * geo_t[1] + trim * geo_t[2]
                new_gt[3] = geo_t[3] + trim * geo_t[4] + trim * geo_t[5]
                new_gt = tuple(new_gt)
            else:
                out_r, out_g, out_b = r_arr, g_arr, b_arr
                out_rows, out_cols = r_shape, c_shape
                new_gt = geo_t

            driver = gdal.GetDriverByName('GTiff')
            out_ds = driver.Create(filepath, out_cols, out_rows, 3, gdal.GDT_Byte)
            out_ds.SetGeoTransform(new_gt)
            out_ds.SetProjection(ds.GetProjection())
            out_ds.GetRasterBand(1).WriteArray(out_r)
            out_ds.GetRasterBand(2).WriteArray(out_g)
            out_ds.GetRasterBand(3).WriteArray(out_b)
            out_ds.FlushCache()
            out_ds = None

        # ====== ステレオ生成処理 ======
        if output_type > 0:
            feedback.setProgressText("4/4: Generating Stereo Image...")
            
            # リサンプリング済みの高解像度データ群を使用
            curr_dem = dem
            curr_rows, curr_cols = rows, cols
            curr_dx = dx
            curr_gt = gt
            curr_trim = radius
            
            R_L, G_L, B_L = R.copy(), G.copy(), B.copy()
            
            dem_min = np.nanmin(curr_dem)
            dem_valid = np.nan_to_num(curr_dem, nan=dem_min)
            
            shift = (dem_valid - dem_min) * exaggeration / curr_dx
            shift = np.round(shift).astype(int)
            
            Y, X = np.indices((curr_rows, curr_cols))
            Z_flat = dem_valid.flatten()
            sort_idx = np.argsort(Z_flat)
            
            X_s = X.flatten()[sort_idx]
            Y_s = Y.flatten()[sort_idx]
            S_s = shift.flatten()[sort_idx]
            
            R_s = R_L.flatten()[sort_idx]
            G_s = G_L.flatten()[sort_idx]
            B_s = B_L.flatten()[sort_idx]
            
            R_R_canvas = np.zeros((curr_rows, curr_cols), dtype=np.uint8)
            G_R_canvas = np.zeros((curr_rows, curr_cols), dtype=np.uint8)
            B_R_canvas = np.zeros((curr_rows, curr_cols), dtype=np.uint8)
            written_R = np.zeros((curr_rows, curr_cols), dtype=bool)
            
            X_R = X_s - S_s
            valid_R = (X_R >= 0) & (X_R < curr_cols)
            
            R_R_canvas[Y_s[valid_R], X_R[valid_R]] = R_s[valid_R]
            G_R_canvas[Y_s[valid_R], X_R[valid_R]] = G_s[valid_R]
            B_R_canvas[Y_s[valid_R], X_R[valid_R]] = B_s[valid_R]
            written_R[Y_s[valid_R], X_R[valid_R]] = True
            
            def fill_holes(arr, written, c_cols):
                out = arr.copy()
                w = written.copy()
                for c in range(1, c_cols):
                    hole = ~w[:, c]
                    out[hole, c] = out[hole, c - 1]
                    w[hole, c] = w[hole, c - 1]
                for c in range(c_cols-2, -1, -1):
                    hole = ~w[:, c]
                    out[hole, c] = out[hole, c + 1]
                    w[hole, c] = w[hole, c + 1]
                return out

            R_R = fill_holes(R_R_canvas, written_R, curr_cols)
            G_R = fill_holes(G_R_canvas, written_R, curr_cols)
            B_R = fill_holes(B_R_canvas, written_R, curr_cols)

            if output_type == 1:
                save_tiff(output_file, R_L, G_R, B_R, curr_rows, curr_cols, curr_gt, curr_trim)
                results = {self.OUTPUT: output_file}
            elif output_type == 2:
                save_tiff(output_file, R_L, G_L, B_L, curr_rows, curr_cols, curr_gt, curr_trim)
                if output_right_file:
                    save_tiff(output_right_file, R_R, G_R, B_R, curr_rows, curr_cols, curr_gt, curr_trim)
                    results = {self.OUTPUT: output_file, self.OUTPUT_RIGHT: output_right_file}
                else:
                    results = {self.OUTPUT: output_file}
            elif output_type == 3:
                save_tiff(output_file, R_R, G_R, B_R, curr_rows, curr_cols, curr_gt, curr_trim)
                if output_right_file:
                    save_tiff(output_right_file, R_L, G_L, B_L, curr_rows, curr_cols, curr_gt, curr_trim)
                    results = {self.OUTPUT: output_file, self.OUTPUT_RIGHT: output_right_file}
                else:
                    results = {self.OUTPUT: output_file}
        else:
            save_tiff(output_file, R, G, B, rows, cols, gt, radius)
            results = {self.OUTPUT: output_file}

        feedback.setProgress(100)
        return results