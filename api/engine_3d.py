"""
Módulo de Geração de Capas Interativas em 3D (WebGL)
=====================================================
Converte a capa gerada ou o E-book final num arquivo .html
interativo que desenha um livro em 3D giratório no navegador.
"""

import base64
import os

def generate_3d_html_cover(cover_image_path: str, title: str, output_html_path: str) -> str:
    """Gera um arquivo HTML contendo um motor Three.js para renderizar o livro realístico em 3D."""
    
    if not os.path.exists(cover_image_path):
        return None
        
    with open(cover_image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
        img_data_uri = f"data:image/jpeg;base64,{encoded_string}"
        
    html_code = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Capa 3D Interativa: {title}</title>
    <style>
        body {{ margin: 0; overflow: hidden; background: #1a1a2e; }}
        canvas {{ width: 100vw; height: 100vh; display: block; }}
        #info {{ position: absolute; top: 20px; width: 100%; text-align: center; color: white; font-family: sans-serif; pointer-events: none; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }}
    </style>
    <!-- Three.js Library -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="info"><h1>📖 {title}</h1><p>Clique e arraste para explorar em 3D</p></div>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;

        // Geometria do Livro (Largura, Altura, Espessura)
        const geometry = new THREE.BoxGeometry(3, 4.5, 0.6);
        
        // Texturas
        const textureLoader = new THREE.TextureLoader();
        const coverTexture = textureLoader.load("{img_data_uri}");
        
        // Materiais para cada lado [Direita, Esquerda, Cima, Baixo, Frente(Capa), Tras(Contracapa)]
        const pageMaterial = new THREE.MeshStandardMaterial({{ color: 0xffffee, roughness: 0.8 }});
        const coverMaterial = new THREE.MeshStandardMaterial({{ map: coverTexture, roughness: 0.2, metalness: 0.1 }});
        const backMaterial = new THREE.MeshStandardMaterial({{ color: 0x111111, roughness: 0.5 }});
        
        const materials = [
            pageMaterial, // right side (pages)
            backMaterial, // left side (spine)
            pageMaterial, // top (pages)
            pageMaterial, // bottom (pages)
            coverMaterial, // front
            backMaterial  // back
        ];

        const book = new THREE.Mesh(geometry, materials);
        scene.add(book);

        // Luzes
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);
        
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(5, 5, 5);
        scene.add(dirLight);

        camera.position.z = 6;
        book.rotation.y = -0.3; // Inicial angulado

        // Animação
        function animate() {{
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }}
        
        window.addEventListener('resize', onWindowResize, false);
        function onWindowResize() {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }}
        
        animate();
    </script>
</body>
</html>"""

    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_code)
        
    return output_html_path
