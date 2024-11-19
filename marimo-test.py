import marimo

__generated_with = "0.9.20"
app = marimo.App()


@app.cell
def __():
    import marimo as mo
    from scipy.optimize import fsolve
    return fsolve, mo


@app.cell
def __(fsolve):
    def f(x):
        return x**2 - 6*x + 8

    guess = 3
    res = fsolve(f, guess)
    return f, guess, res


if __name__ == "__main__":
    app.run()
