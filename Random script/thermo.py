t_in = 273.15 -13
tpe = 25 + 273.15
tpeo = 0
tenv = 30 + 273.15
Ri = (1/8) + (0.03/0.035)

while(abs(tpe -tpeo) < 0.001):
    Kre = 0.91 * (5.67e-8)*(tenv**4 - tpe**4) / (tenv-tpe)
    tpeo = tpe
    tpe = ((0.09*800) + (15+Kre)*tenv + (t_in / Ri)) / (15 + Kre + (1/Ri) )
    print(f"Kre: {Kre} | Tpe: {tpe}")
else:
    print("flux", (tpe - t_in)*10/Ri)