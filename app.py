from flask import Flask, render_template, request, jsonify
import ipaddress

app = Flask(__name__)

def obtener_clase(ip):
    octeto = int(ip.split('.')[0])
    if 0 <= octeto <= 127:
        return 'A', 8
    elif 128 <= octeto <= 191:
        return 'B', 16
    elif 192 <= octeto <= 223:
        return 'C', 24
    else:
        return None, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calcular_subredes', methods=['POST'])
def calcular_subredes():
    try:
        ip_str = request.form['ip']
        num_subredes = int(request.form['num_subredes'])

        # Validar la dirección IP y obtener su clase
        ip = ipaddress.IPv4Address(ip_str)
        clase, prefixlen = obtener_clase(ip_str)
        if clase is None:
            raise ValueError("Dirección IP fuera de rango de Clase A, B o C.")

        # Validar el número de subredes
        if num_subredes <= 0:
            raise ValueError("El número de subredes debe ser mayor que cero.")

        # Crear la red IPv4 con la máscara de subred predeterminada de su clase
        network = ipaddress.IPv4Network(f"{ip_str}/{prefixlen}", strict=False)
        new_prefix = prefixlen + (num_subredes - 1).bit_length()

        # Validar que la nueva máscara de subred no exceda el tamaño máximo de la subred
        if new_prefix > 30:  # Límite de subredes en una red de clase A, B, C
            raise ValueError("El número de subredes es demasiado grande para esta clase de red.")

        # Calcular las subredes
        subredes = list(network.subnets(new_prefix=new_prefix))[:num_subredes]

        resultados = []
        for i, subnet in enumerate(subredes):
            resultados.append({
                "subred": f"Subred {i + 1}",
                "ip_inicial": str(subnet.network_address),
                "ip_final": str(subnet.broadcast_address),
                "mascara": str(subnet.netmask),
                "clase": clase
            })

        return jsonify(resultados)
    except ValueError as e:
        return jsonify({"error": str(e)})

@app.route('/identificar_red', methods=['POST'])
def identificar_red():
    try:
        subred = request.form['subred']
        objeto_subred = ipaddress.ip_network(subred, strict=False)
        red = str(objeto_subred.network_address)
        return jsonify({"red": red})
    except ValueError as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='192.168.27.1', port=5000, debug=True)