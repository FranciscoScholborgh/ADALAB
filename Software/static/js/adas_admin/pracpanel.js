var procedimientos = {};
var proc_count=1;

function panelProcedimiento() {
    $("#proc_modal").modal();
    $("#procmod_title").val(" Agregar procedimiento ");
    $("#proc_desc").val('');
    $("#proc_meas").val('');
    $("#proc_unit").val('');
    $("#proc_unit").click(add_procedimiento);
}

function add_procedimiento(id_proc) {
    var descrip = $("#proc_desc").val();
    var measure = $("#proc_meas").val();
    var unit = $("#proc_unit").val();
    if (descrip === '') {
        alert("Debe agregar una descripción a la práctica");
        return false;
    }
    if (measure === '') {
        alert("Debe agregar las medidas a realizar a la práctica");
        return false;
    }
    if (unit === '') {
        alert("Debe agregar las unidades de las medidas descripción a la práctica");
        return false;
    }
    var measures = measure.split(',');
    var units = unit.split(',');

    if (measures.length != units.length){
        alert("Debe ingresar la misma cantidad de unidades que de medidas");
        return false;
    }

    if(id_proc === undefined){
        var id = `proc_${proc_count}`;
        var min = descrip.slice(0,17);
        $("#procedimientos").append(`
            <div id="${id}" class="d-flex justify-content-between" style="padding-top: 25px;">
                <h4 id="text${id}}" class="text-left">${min}...</h4>
                <div>
                    <button class="btn btn-secondary rounded" title="detalles" onclick="view_proc(${id})">
                        <i class="fa fa-eye fa-lg" aria-hidden="true"></i>
                    </button>
                    <button class="btn btn-secondary rounded" title="remover" onclick="remove_proc(${id})">
                        <i class="fa fa-trash fa-lg" aria-hidden="true"></i>
                    </button>
                </div>
            </div>`
        );
    }   
    procedimientos['proc${id}'] = {descripcion:descrip, medidas:measures, unidades:units}
}

function view_proc(id_proc) {
    var proc = procedimientos[id_proc];
    $("#procmod_title").val("Información de procedimiento");
    $("#proc_desc").val(proc.descripcion);
    $("#proc_meas").val(proc.medidas);
    $("#proc_unit").val(proc.unidades);
    $("#proc_btn").click(add_procedimiento(id_proc));
}